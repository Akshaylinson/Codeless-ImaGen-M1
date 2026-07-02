from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from ..core.security import get_current_user
from ..database.sqlite import db_session
from ..schemas.jobs import StartEditRequest, StartEditResponse
from ..services.job_service import JobService
from ..services.pipeline_service import PipelineService


router = APIRouter(prefix="/api/edit", tags=["edit"])
job_service = JobService()
pipeline_service = PipelineService()


@router.post("/start", response_model=StartEditResponse)
def start_edit(
    payload: StartEditRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> StartEditResponse:
    with db_session() as connection:
        image = connection.execute("SELECT * FROM images WHERE id = ?", (payload.image_id,)).fetchone()
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    job_id = job_service.create_job(current_user["user_id"], payload.image_id, payload.instruction)
    background_tasks.add_task(pipeline_service.process_job, job_id, Path(image["storage_path"]), payload.instruction)
    with db_session() as connection:
        connection.execute(
            "INSERT INTO edit_requests (job_id, intent_json) VALUES (?, ?)",
            (job_id, payload.instruction),
        )
    return StartEditResponse(job_id=job_id)
