from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from ..core.config import settings
from ..utils.paths import sanitize_filename
from ..utils.image_processing import create_thumbnail, save_image


@dataclass(slots=True)
class StoredImage:
    image_path: Path
    thumbnail_path: Path


class StorageService:
    def save_upload(self, image_id: int, filename: str, data: bytes, image: Image.Image) -> StoredImage:
        safe_name = f"{image_id:08d}_{sanitize_filename(filename)}"
        image_path = settings.uploads_dir / safe_name
        thumbnail_path = settings.thumbnails_dir / f"{image_id:08d}_thumb.jpg"
        image_path.write_bytes(data)
        thumb = create_thumbnail(image)
        save_image(thumb.convert("RGB"), thumbnail_path)
        return StoredImage(image_path=image_path, thumbnail_path=thumbnail_path)

    def save_generated(self, job_id: int, image: Image.Image) -> Path:
        output_path = settings.generated_dir / f"job_{job_id:08d}.png"
        save_image(image, output_path)
        return output_path

    def save_mask(self, job_id: int, mask: Image.Image) -> Path:
        mask_path = settings.masks_dir / f"job_{job_id:08d}_mask.png"
        save_image(mask.convert("L"), mask_path)
        return mask_path

