from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .api.auth import router as auth_router
from .api.images import router as images_router
from .api.edit import router as edit_router
from .api.jobs import router as jobs_router
from .api.history import router as history_router
from .api.health import router as health_router
from .core.config import settings, ensure_directories, write_frontend_config
from .core.logging import configure_logging
from .core.middleware import SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from .database.sqlite import init_db


configure_logging()
ensure_directories()
init_db()
write_frontend_config()

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
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

app.mount(settings.static_url, StaticFiles(directory=settings.frontend_dir / "assets", html=False), name="static")
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir, html=False), name="uploads")
app.mount("/generated", StaticFiles(directory=settings.generated_dir, html=False), name="generated")
app.mount("/masks", StaticFiles(directory=settings.masks_dir, html=False), name="masks")
app.mount("/thumbnails", StaticFiles(directory=settings.thumbnails_dir, html=False), name="thumbnails")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(settings.frontend_dir / "index.html")


@app.get("/dashboard.html")
def dashboard_page() -> FileResponse:
    return FileResponse(settings.frontend_dir / "dashboard.html")


@app.get("/editor.html")
def editor_page() -> FileResponse:
    return FileResponse(settings.frontend_dir / "editor.html")


@app.get("/gallery.html")
def gallery_page() -> FileResponse:
    return FileResponse(settings.frontend_dir / "gallery.html")


@app.get("/admin.html")
def admin_page() -> FileResponse:
    return FileResponse(settings.frontend_dir / "admin.html")


@app.get("/config.js")
def runtime_config() -> PlainTextResponse:
    return PlainTextResponse((settings.frontend_dir / "config.js").read_text(encoding="utf-8"), media_type="application/javascript")


@app.on_event("startup")
def startup() -> None:
    write_frontend_config()
    logger.info("Application startup complete")


@app.on_event("shutdown")
def shutdown() -> None:
    logger.info("Application shutdown complete")
