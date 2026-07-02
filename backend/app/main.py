from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.auth import router as auth_router
from .api.images import router as images_router
from .api.edit import router as edit_router
from .api.jobs import router as jobs_router
from .api.history import router as history_router
from .api.health import router as health_router
from .core.config import settings, ensure_directories
from .core.logging import configure_logging
from .core.middleware import SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from .database.sqlite import init_db


configure_logging()
ensure_directories()
init_db()

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)

app.include_router(auth_router)
app.include_router(images_router)
app.include_router(edit_router)
app.include_router(jobs_router)
app.include_router(history_router)
app.include_router(health_router)

if settings.frontend_dir.exists():
    app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")


@app.on_event("startup")
def startup() -> None:
    logger.info("Application startup complete")


@app.on_event("shutdown")
def shutdown() -> None:
    logger.info("Application shutdown complete")

