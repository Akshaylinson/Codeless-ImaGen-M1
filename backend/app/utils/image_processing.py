from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from ..core.config import settings


@dataclass(slots=True)
class LoadedImage:
    image: Image.Image
    width: int
    height: int


def load_image(data: bytes) -> LoadedImage:
    image = Image.open(BytesIO(data)).convert("RGB")
    width, height = image.size
    if width > settings.max_image_dimension or height > settings.max_image_dimension:
        image.thumbnail((settings.max_image_dimension, settings.max_image_dimension), Image.Resampling.LANCZOS)
        width, height = image.size
    return LoadedImage(image=image, width=width, height=height)


def save_image(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def create_thumbnail(image: Image.Image, size: tuple[int, int] = (512, 512)) -> Image.Image:
    thumb = image.copy()
    thumb.thumbnail(size, Image.Resampling.LANCZOS)
    return ImageOps.contain(thumb, size, method=Image.Resampling.LANCZOS)


def create_mask_preview(image: Image.Image, mask: Image.Image) -> Image.Image:
    overlay = image.convert("RGBA")
    mask_rgba = Image.new("RGBA", overlay.size, (255, 0, 0, 0))
    red = Image.new("RGBA", overlay.size, (255, 0, 0, 120))
    mask_rgba.paste(red, mask=mask.convert("L"))
    return Image.alpha_composite(overlay, mask_rgba)


def apply_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    return Image.composite(image, Image.new("RGB", image.size, (0, 0, 0)), mask.convert("L"))


def bbox_to_mask(size: tuple[int, int], bbox: tuple[int, int, int, int]) -> Image.Image:
    from PIL import ImageDraw

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(bbox, fill=255)
    return mask


def average_border_color(image: Image.Image, bbox: tuple[int, int, int, int]) -> tuple[int, int, int]:
    arr = np.array(image)
    x1, y1, x2, y2 = bbox
    pad = 12
    regions = []
    if y1 > pad:
        regions.append(arr[max(0, y1 - pad):y1, x1:x2])
    if y2 < image.height - pad:
        regions.append(arr[y2:min(image.height, y2 + pad), x1:x2])
    if x1 > pad:
        regions.append(arr[y1:y2, max(0, x1 - pad):x1])
    if x2 < image.width - pad:
        regions.append(arr[y1:y2, x2:min(image.width, x2 + pad)])
    pixels = np.concatenate([r.reshape(-1, 3) for r in regions if r.size], axis=0) if regions else arr.reshape(-1, 3)
    color = pixels.mean(axis=0)
    return tuple(int(v) for v in color)


def soft_inpaint(image: Image.Image, mask: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    blurred = image.filter(ImageFilter.GaussianBlur(radius=12))
    base = Image.new("RGB", image.size, average_border_color(image, bbox))
    blended = Image.composite(blurred, base, mask.convert("L"))
    return Image.composite(blended, image, Image.eval(mask.convert("L"), lambda p: 255 - p))

