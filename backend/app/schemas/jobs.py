from __future__ import annotations

from pydantic import BaseModel, Field


class StartEditRequest(BaseModel):
    image_id: int
    instruction: str = Field(min_length=1, max_length=4000)


class StartEditResponse(BaseModel):
    job_id: int


class JobResponse(BaseModel):
    id: int
    image_id: int
    instruction: str
    status: str
    progress: int
    error_message: str | None = None
    output_path: str | None = None
    processing_time: float | None = None
    created_at: str
    updated_at: str


class HistoryResponse(BaseModel):
    jobs: list[JobResponse]

