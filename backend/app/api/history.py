from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.config import settings
from ..core.security import get_current_user
from ..schemas.jobs import HistoryResponse, JobResponse
from ..services.job_service import JobService


router = APIRouter(prefix=f"{settings.api_prefix}/history", tags=["history"])
job_service = JobService()


@router.get("", response_model=HistoryResponse)
def history(current_user: dict = Depends(get_current_user)) -> HistoryResponse:
    jobs = [
        JobResponse(
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
        for row in job_service.list_jobs()
    ]
    return HistoryResponse(jobs=jobs)
