from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from .config import settings, ensure_directories


def configure_logging() -> None:
    ensure_directories()
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    system_handler = RotatingFileHandler(
        settings.logs_dir / "system.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    inference_handler = RotatingFileHandler(
        settings.logs_dir / "inference.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    error_handler = RotatingFileHandler(
        settings.logs_dir / "error.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )

    for handler, level in [
        (system_handler, logging.INFO),
        (inference_handler, logging.INFO),
        (error_handler, logging.ERROR),
    ]:
        handler.setFormatter(formatter)
        handler.setLevel(level)
        root.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    root.addHandler(console)

