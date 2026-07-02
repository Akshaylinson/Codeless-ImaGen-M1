from __future__ import annotations

from pathlib import Path
import re


SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = SAFE_FILENAME_RE.sub("_", name).strip("._")
    return name or "image"


def ensure_within(base: Path, candidate: Path) -> Path:
    resolved_base = base.resolve()
    resolved_candidate = candidate.resolve()
    if resolved_base not in resolved_candidate.parents and resolved_candidate != resolved_base:
        raise ValueError("Path traversal attempt detected")
    return resolved_candidate

