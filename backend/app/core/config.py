from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import DotEnvSettingsSource, EnvSettingsSource, PydanticBaseSettingsSource


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
STORAGE_DIR = ROOT_DIR / "storage"
LOG_DIR = ROOT_DIR / "logs"
MODELS_DIR = ROOT_DIR / "models"


class _CsvOriginsMixin:
    def _parse_allowed_origins(self, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


class CsvAwareEnvSettingsSource(_CsvOriginsMixin, EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: Any, value: Any, value_is_complex: bool) -> Any:
        if field_name == "allowed_origins":
            return self._parse_allowed_origins(value)
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class CsvAwareDotEnvSettingsSource(_CsvOriginsMixin, DotEnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: Any, value: Any, value_is_complex: bool) -> Any:
        if field_name == "allowed_origins":
            return self._parse_allowed_origins(value)
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    app_name: str = Field(default="CodelessAI Smart Image Editor", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    public_base_url: str = Field(default="", alias="PUBLIC_BASE_URL")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    frontend_url: str = Field(default="", alias="FRONTEND_URL")
    static_url: str = Field(default="/static", alias="STATIC_URL")
    allowed_origins: list[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")
    enable_https: bool = Field(default=False, alias="ENABLE_HTTPS")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    access_token_ttl_minutes: int = Field(default=480, alias="ACCESS_TOKEN_TTL_MINUTES")
    max_upload_mb: int = Field(default=20, alias="MAX_UPLOAD_MB")
    max_image_dimension: int = Field(default=2048, alias="MAX_IMAGE_DIMENSION")
    max_concurrent_jobs: int = Field(default=2, alias="MAX_CONCURRENT_JOBS")
    models_dir: Path = Field(default=MODELS_DIR, alias="MODELS_DIR")
    intent_model_path: Path = Field(default=MODELS_DIR / "Qwen2.5-3B-Instruct-GGUF.gguf", alias="INTENT_MODEL_PATH")
    intent_model_n_ctx: int = Field(default=4096, alias="INTENT_MODEL_N_CTX")
    intent_model_n_threads: int = Field(default=4, alias="INTENT_MODEL_N_THREADS")
    intent_model_n_gpu_layers: int = Field(default=0, alias="INTENT_MODEL_N_GPU_LAYERS")
    intent_model_max_tokens: int = Field(default=256, alias="INTENT_MODEL_MAX_TOKENS")
    intent_model_temperature: float = Field(default=0.0, alias="INTENT_MODEL_TEMPERATURE")
    intent_model_top_p: float = Field(default=0.95, alias="INTENT_MODEL_TOP_P")
    database_path: Path = Field(default=STORAGE_DIR / "codelessai.sqlite3", alias="DATABASE_PATH")
    uploads_dir: Path = Field(default=STORAGE_DIR / "uploads", alias="UPLOADS_DIR")
    generated_dir: Path = Field(default=STORAGE_DIR / "generated", alias="GENERATED_DIR")
    masks_dir: Path = Field(default=STORAGE_DIR / "masks", alias="MASKS_DIR")
    thumbnails_dir: Path = Field(default=STORAGE_DIR / "thumbnails", alias="THUMBNAILS_DIR")
    temp_dir: Path = Field(default=STORAGE_DIR / "temp", alias="TEMP_DIR")
    logs_dir: Path = Field(default=LOG_DIR, alias="LOGS_DIR")
    frontend_dir: Path = Field(default=FRONTEND_DIR, alias="FRONTEND_DIR")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_max_requests: int = Field(default=120, alias="RATE_LIMIT_MAX_REQUESTS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            CsvAwareEnvSettingsSource(settings_cls),
            CsvAwareDotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    @field_validator("api_prefix", "static_url", mode="before")
    @classmethod
    def normalize_slash_prefix(cls, value: object) -> str:
        text = str(value or "").strip()
        if not text.startswith("/"):
            text = "/" + text
        return text.rstrip("/") or "/"

    @field_validator("public_base_url", "frontend_url", mode="before")
    @classmethod
    def trim_trailing_slash(cls, value: object) -> str:
        return str(value or "").rstrip("/")


settings = Settings()


def ensure_directories() -> None:
    for directory in [
        settings.models_dir,
        settings.uploads_dir,
        settings.generated_dir,
        settings.masks_dir,
        settings.thumbnails_dir,
        settings.temp_dir,
        settings.logs_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def build_frontend_config() -> str:
    payload = {
        "APP_NAME": settings.app_name,
        "APP_ENV": settings.app_env,
        "BASE_URL": settings.frontend_url,
        "API_BASE_URL": settings.public_base_url,
        "STATIC_BASE_URL": settings.public_base_url,
        "PUBLIC_BASE_URL": settings.public_base_url,
        "FRONTEND_URL": settings.frontend_url,
        "API_PREFIX": settings.api_prefix,
        "STATIC_URL": settings.static_url,
        "ENABLE_HTTPS": settings.enable_https,
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    return f"""const raw = {payload_json};
const defaultOrigin = window.location.origin;

window.APP_CONFIG = {{
  APP_NAME: raw.APP_NAME || 'CodelessAI Smart Image Editor',
  APP_ENV: raw.APP_ENV || 'development',
  BASE_URL: raw.BASE_URL || defaultOrigin,
  API_BASE_URL: raw.API_BASE_URL ? `${{raw.API_BASE_URL}}${{raw.API_PREFIX || '/api'}}` : `${{defaultOrigin}}/api`,
  STATIC_BASE_URL: raw.STATIC_BASE_URL ? `${{raw.STATIC_BASE_URL}}${{raw.STATIC_URL || '/static'}}` : `${{defaultOrigin}}/static`,
  PUBLIC_BASE_URL: raw.PUBLIC_BASE_URL || defaultOrigin,
  FRONTEND_URL: raw.FRONTEND_URL || defaultOrigin,
  API_PREFIX: raw.API_PREFIX || '/api',
  STATIC_URL: raw.STATIC_URL || '/static',
  ENABLE_HTTPS: Boolean(raw.ENABLE_HTTPS),
}};
"""


def write_frontend_config() -> Path:
    ensure_directories()
    config_path = settings.frontend_dir / "config.js"
    config_path.write_text(build_frontend_config(), encoding="utf-8")
    return config_path
