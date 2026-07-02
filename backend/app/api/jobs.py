from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..core.config import settings
from ..core.security import get_current_user
from ..schemas.jobs import JobResponse
from ..services.job_service import JobService


router = APIRouter(prefix=f"{settings.api_prefix}/jobs", tags=["jobs"])
job_service = JobService()


def _to_response(row: dict) -> JobResponse:
    return JobResponse(
        id=row["id"],
        image_id=row["image_id"],
        instruction=row["instruction"],
        status=row["status"],
        progress=row["progress"],
        error_message=row["error_message"],
        output_path=row["output_path"],
        processing_time=row["processing_time"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, current_user: dict = Depends(get_current_user)) -> JobResponse:
    row = job_service.get_job(job_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _to_response(row)


@router.get("/{job_id}/result")
def get_job_result(job_id: int, current_user: dict = Depends(get_current_user)) -> Response:
    row = job_service.get_job(job_id)
    if not row or not row["output_path"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not ready")
    return Response(content=Path(row["output_path"]).read_bytes(), media_type="image/png")


@router.delete("/{job_id}")
def delete_job(job_id: int, current_user: dict = Depends(get_current_user)) -> dict[str, str]:
    job_service.delete_job(job_id)
    return {"status": "deleted"}
