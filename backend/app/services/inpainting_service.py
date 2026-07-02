from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .base import ModelService
from ..utils.image_processing import save_image, soft_inpaint


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class InpaintingResult:
    output_path: Path


class InpaintingService(ModelService):
    model_name = "Stable Diffusion 1.5 Inpainting ONNX"

    def predict(
        self,
        image: Image.Image,
        mask: Image.Image,
        bbox: tuple[int, int, int, int],
        output_path: Path,
        instruction: str,
        replacement_prompt: str,
    ) -> InpaintingResult:
        edited = soft_inpaint(image, mask, bbox)
        save_image(edited, output_path)
        result = InpaintingResult(output_path=output_path)
        logger.info("Inpainting result saved: %s", result)
        return result

