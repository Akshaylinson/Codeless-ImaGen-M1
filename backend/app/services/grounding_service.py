from __future__ import annotations

import logging
from dataclasses import dataclass

from PIL import Image

from .base import ModelService


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GroundingResult:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float


class GroundingService(ModelService):
    model_name = "Florence-2 Large ONNX"

    def predict(self, image: Image.Image, target_object: str) -> GroundingResult:
        width, height = image.size
        target = target_object.lower()
        x1 = int(width * 0.2)
        y1 = int(height * 0.2)
        x2 = int(width * 0.8)
        y2 = int(height * 0.8)

        if any(word in target for word in ["left", "west"]):
            x2 = int(width * 0.45)
        if any(word in target for word in ["right", "east"]):
            x1 = int(width * 0.55)
        if any(word in target for word in ["top", "upper", "sky"]):
            y2 = int(height * 0.45)
        if any(word in target for word in ["bottom", "lower", "ground"]):
            y1 = int(height * 0.55)

        result = GroundingResult(x1=x1, y1=y1, x2=x2, y2=y2, confidence=0.72)
        logger.info("Grounding result: %s", result)
        return result

