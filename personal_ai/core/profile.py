"""Lightweight user preference persistence."""

from __future__ import annotations

import json
from typing import Any, Dict

from .config import SETTINGS


def load_profile() -> Dict[str, Any]:
    if not SETTINGS.profile_file.exists():
        return {"user_name": "", "preferred_mode": "", "last_intent": ""}
    try:
        with SETTINGS.profile_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
            if isinstance(payload, dict):
                return payload
    except Exception:
        return {"user_name": "", "preferred_mode": "", "last_intent": ""}
    return {"user_name": "", "preferred_mode": "", "last_intent": ""}


def save_profile(profile: Dict[str, Any]) -> None:
    SETTINGS.profile_file.parent.mkdir(parents=True, exist_ok=True)
    with SETTINGS.profile_file.open("w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2)
