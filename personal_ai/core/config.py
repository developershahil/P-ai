"""Centralized runtime configuration with optional .env support."""

from __future__ import annotations

import os
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR.parent / ".env"

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv
else:
    def load_dotenv(_path: Path) -> bool:
        return False

# Load environment variables from project root .env if available.
load_dotenv(ENV_PATH)


def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}


def detect_mode() -> str:
    has_speech = find_spec("speech_recognition") is not None
    has_tts = find_spec("pyttsx3") is not None
    return "local" if has_speech and has_tts else "dev"


@dataclass(frozen=True)
class Settings:
    mode: str
    conf_threshold: float
    auto_learn: bool
    auto_learn_min_conf: float
    model_improvement_threshold: float
    model_random_state: int
    api_key: str
    log_level: str
    log_file: Path
    error_log_file: Path
    profile_file: Path


SETTINGS = Settings(
    mode=os.getenv("MODE") or detect_mode(),
    conf_threshold=float(os.getenv("CONF_THRESHOLD", "0.55")),
    auto_learn=_env_flag("AUTO_LEARN", "1"),
    auto_learn_min_conf=float(os.getenv("AUTO_LEARN_MIN_CONF", "0.75")),
    model_improvement_threshold=float(os.getenv("MODEL_IMPROVEMENT_THRESHOLD", "0.01")),
    model_random_state=int(os.getenv("MODEL_RANDOM_STATE", "42")),
    api_key=os.getenv("API_KEY", ""),
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=BASE_DIR / "logs" / "app.log",
    error_log_file=BASE_DIR / "logs" / "error.log",
    profile_file=BASE_DIR / "data" / "profile.json",
)

MODE = SETTINGS.mode
CONF_THRESHOLD = SETTINGS.conf_threshold
AUTO_LEARN = SETTINGS.auto_learn
AUTO_LEARN_MIN_CONF = SETTINGS.auto_learn_min_conf
