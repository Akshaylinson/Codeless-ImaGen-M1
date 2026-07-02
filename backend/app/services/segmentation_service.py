from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .base import ModelService
from ..utils.image_processing import bbox_to_mask, create_mask_preview, save_image


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SegmentationResult:
    mask_path: Path
    preview_path: Path


class SegmentationService(ModelService):
    model_name = "MobileSAM ONNX"

    def predict(
        self,
        image: Image.Image,
        bbox: tuple[int, int, int, int],
        mask_path: Path,
        preview_path: Path,
    ) -> SegmentationResult:
        mask = bbox_to_mask(image.size, bbox)
        preview = create_mask_preview(image, mask)
        save_image(mask, mask_path)
        save_image(preview.convert("RGB"), preview_path)
        result = SegmentationResult(mask_path=mask_path, preview_path=preview_path)
        logger.info("Segmentation result saved: %s", result)
        return result

