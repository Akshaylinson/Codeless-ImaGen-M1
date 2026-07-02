from __future__ import annotations

import logging
import time
from pathlib import Path

from PIL import Image

from .intent_service import IntentService
from .grounding_service import GroundingService
from .segmentation_service import SegmentationService
from .inpainting_service import InpaintingService
from .storage_service import StorageService
from .job_service import JobService
from ..database.sqlite import db_session
from ..utils.image_processing import load_image


logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self) -> None:
        self.job_service = JobService()
        self.storage_service = StorageService()

    def process_job(self, job_id: int, image_path: Path, instruction: str) -> None:
        start = time.time()
        try:
            self.job_service.update_job(job_id, status="processing", progress=10)
            loaded = load_image(image_path.read_bytes())

            with IntentService() as intent_service:
                intent = intent_service.predict(instruction)
            self.job_service.update_job(job_id, progress=30)

            with GroundingService() as grounding_service:
                grounding = grounding_service.predict(loaded.image, intent.target_object)
            self.job_service.update_job(job_id, progress=50)

            mask_path = image_path.parent / f"job_{job_id:08d}_mask.png"
            preview_path = image_path.parent / f"job_{job_id:08d}_mask_preview.png"
            with SegmentationService() as segmentation_service:
                segmentation_service.predict(
                    loaded.image,
                    (grounding.x1, grounding.y1, grounding.x2, grounding.y2),
                    mask_path,
                    preview_path,
                )
            self.job_service.update_job(job_id, progress=70)

            with Image.open(mask_path) as mask_image:
                with InpaintingService() as inpainting_service:
                    result = inpainting_service.predict(
                        loaded.image,
                        mask_image.convert("L"),
                        (grounding.x1, grounding.y1, grounding.x2, grounding.y2),
                        image_path.parent.parent / "generated" / f"job_{job_id:08d}.png",
                        instruction,
                        intent.replacement_object or intent.target_object,
                    )

            processing_time = round(time.time() - start, 3)
            self.job_service.set_completed(job_id, str(result.output_path), processing_time)
            self.job_service.update_job(job_id, progress=100)
            with db_session() as connection:
                connection.execute(
                    "INSERT INTO generated_images (job_id, path) VALUES (?, ?)",
                    (job_id, str(result.output_path)),
                )
            logger.info("Job %s completed in %ss", job_id, processing_time)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Job %s failed", job_id)
            self.job_service.set_failed(job_id, str(exc))

