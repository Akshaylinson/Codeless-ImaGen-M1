from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
STORAGE_DIR = ROOT_DIR / "storage"
LOG_DIR = ROOT_DIR / "logs"


@dataclass(slots=True)
class Settings:
    app_name: str = "CodelessAI Smart Image Editor"
    environment: str = os.getenv("APP_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_ttl_minutes: int = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "480"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "20"))
    max_image_dimension: int = int(os.getenv("MAX_IMAGE_DIMENSION", "2048"))
    max_concurrent_jobs: int = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
    database_path: Path = ROOT_DIR / "storage" / "codelessai.sqlite3"
    uploads_dir: Path = STORAGE_DIR / "uploads"
    generated_dir: Path = STORAGE_DIR / "generated"
    masks_dir: Path = STORAGE_DIR / "masks"
    thumbnails_dir: Path = STORAGE_DIR / "thumbnails"
    temp_dir: Path = STORAGE_DIR / "temp"
    logs_dir: Path = LOG_DIR
    frontend_dir: Path = FRONTEND_DIR
    allowed_origins: list[str] = field(default_factory=lambda: ["*"])
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 120
    cors_allow_credentials: bool = True


settings = Settings()


def ensure_directories() -> None:
    for directory in [
        settings.uploads_dir,
        settings.generated_dir,
        settings.masks_dir,
        settings.thumbnails_dir,
        settings.temp_dir,
        settings.logs_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

