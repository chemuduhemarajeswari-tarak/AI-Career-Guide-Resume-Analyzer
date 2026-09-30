"""Small, defensive JSON persistence helpers for the local demo application."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_LOCK = RLock()
DEFAULTS: dict[str, Any] = {
    "users": {},
    "career_plans": {},
    "resume_history": [],
    "saved_resources": [],
    "progress": {},
    "interview_history": [],
    "achievements": {},
    "job_analyses": [],
    "career_plan_history": [],
    "project_history": [],
    "project_recommendations": [],
}


def read_json(name: str, default: Any = None) -> Any:
    path = _DATA_DIR / f"{name}.json"
    fallback = DEFAULTS.get(name, [] if default is None else default)
    with _LOCK:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return fallback.copy() if isinstance(fallback, (dict, list)) else fallback


def write_json(name: str, value: Any) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _DATA_DIR / f"{name}.json"
    with _LOCK:
        handle, temporary = tempfile.mkstemp(prefix=f".{name}-", dir=_DATA_DIR)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(value, stream, indent=2, ensure_ascii=True)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def append_json(name: str, value: Any) -> list[Any]:
    with _LOCK:
        items = read_json(name, [])
        if not isinstance(items, list):
            items = []
        items.append(value)
        write_json(name, items)
        return items


def update_json(name: str, key: str, value: Any) -> dict[str, Any]:
    with _LOCK:
        items = read_json(name, {})
        if not isinstance(items, dict):
            items = {}
        items[key] = value
        write_json(name, items)
        return items
