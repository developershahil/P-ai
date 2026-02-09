# config.py
import os
from importlib.util import find_spec

def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}

def detect_mode() -> str:
    has_speech = find_spec("speech_recognition") is not None
    has_tts = find_spec("pyttsx3") is not None
    return "local" if has_speech and has_tts else "dev"

MODE = os.getenv("MODE") or detect_mode()
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.55"))
AUTO_LEARN = _env_flag("AUTO_LEARN", "1")
AUTO_LEARN_MIN_CONF = float(os.getenv("AUTO_LEARN_MIN_CONF", "0.75"))
