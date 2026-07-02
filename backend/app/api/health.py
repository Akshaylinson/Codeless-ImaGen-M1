from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import APIRouter

from ..core.config import settings
from ..services.job_service import JobService


router = APIRouter(tags=["health"])
job_service = JobService()


def _memory_mb() -> float:
    try:
        import psutil  # type: ignore

        return round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 2)
    except Exception:
        return 0.0


def _cpu_percent() -> float:
    try:
        import psutil  # type: ignore

        return round(psutil.cpu_percent(interval=0.1), 2)
    except Exception:
        return 0.0


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@router.get("/metrics")
def metrics() -> dict[str, object]:
    disk = shutil.disk_usage(settings.database_path.parent)
    jobs = job_service.list_jobs()
    active_jobs = len([job for job in jobs if job["status"] == "processing"])
    return {
        "cpu_usage_percent": _cpu_percent(),
        "ram_usage_mb": _memory_mb(),
        "disk_free_mb": round(disk.free / 1024 / 1024, 2),
        "disk_total_mb": round(disk.total / 1024 / 1024, 2),
        "queue_size": len([job for job in jobs if job["status"] == "queued"]),
        "active_jobs": active_jobs,
    }

