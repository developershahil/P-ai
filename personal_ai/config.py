# config.py
import os

def detect_mode():
    try:
        import speech_recognition  # noqa
        import pyttsx3  # noqa
        return "local"
    except Exception:
        return "dev"

MODE = os.getenv("MODE") or detect_mode()
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.55"))
