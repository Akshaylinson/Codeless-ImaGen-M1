from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ..core.config import settings
from ..core.security import get_current_user
from ..database.sqlite import db_session
from ..schemas.images import UploadImageResponse
from ..services.storage_service import StorageService
from ..utils.file_validation import validate_extension, validate_upload
from ..utils.image_processing import load_image


router = APIRouter(prefix=f"{settings.api_prefix}/images", tags=["images"])
storage_service = StorageService()


@router.post("/upload", response_model=UploadImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> UploadImageResponse:
    validate_extension(file.filename or "image")
    data = await validate_upload(file)
    loaded = load_image(data)
    with db_session() as connection:
        cursor = connection.execute(
            """
            INSERT INTO images (user_id, original_filename, storage_path, mime_type, size_bytes, width, height)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user["user_id"],
                file.filename or "image",
                "",
                file.content_type or "application/octet-stream",
                len(data),
                loaded.width,
                loaded.height,
            ),
        )
        image_id = int(cursor.lastrowid)
        stored = storage_service.save_upload(image_id, file.filename or "image", data, loaded.image)
        connection.execute(
            "UPDATE images SET storage_path = ? WHERE id = ?",
            (str(stored.image_path), image_id),
        )
    return UploadImageResponse(image_id=image_id)
