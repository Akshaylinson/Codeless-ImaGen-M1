from __future__ import annotations

from pydantic import BaseModel


class UploadImageResponse(BaseModel):
    image_id: int


class ImageRecord(BaseModel):
    id: int
    original_filename: str
    storage_path: str
    mime_type: str
    size_bytes: int
    width: int
    height: int
    created_at: str

