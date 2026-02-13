from importlib.util import find_spec
from pathlib import Path

joblib = None
np = None
if find_spec("joblib") is not None:
    import joblib  # type: ignore[assignment]
if find_spec("numpy") is not None:
    import numpy as np  # type: ignore[assignment]

from .config import MODE, CONF_THRESHOLD, AUTO_LEARN, AUTO_LEARN_MIN_CONF
from ..parser import split_commands
from ..entities import extract_entities
from ..actions.app_actions import resolve_app
from ..actions.app_actions import (
    open_app_action, close_app_action, search_action,
    time_action, joke_action, write_file_action, read_file_action,
    reply_action, speak, listen_text
)
from ..learning.collector import log_sample
from ..reminders import schedule_reminder, start_reminder_service


print(f"🔧 Running in {MODE.upper()} mode")

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "intent_model.pkl"
if MODEL_PATH.exists() and joblib is not None:
    model = joblib.load(MODEL_PATH)
else:
    model = None
    if joblib is None:
        print("⚠️ joblib is not installed. Install requirements to enable the model.")
    elif not MODEL_PATH.exists():
        print("⚠️ Model not found. Train it with: python -m personal_ai.ml.train")

RULE_KEYWORDS = {
    "open_app": ["open", "launch", "start"],
    "close_app": ["close", "quit", "exit app", "stop"],
    "search": ["search", "find", "look up", "google"],
    "reminder": ["remind me", "set reminder", "reminder"],
    "time": ["time", "date", "day"],
    "joke": ["joke", "funny"],
    "write_file": ["write", "note", "save"],
    "read_file": ["read", "show notes", "notes"],
    "reply": ["hello", "hi", "hey", "yo", "sup"],
    "exit": ["bye", "exit", "stop assistant", "quit"],
}

start_reminder_service()

def predict_intent_with_confidence(text: str):
    text = text.lower()
    if model is None or np is None:
        for intent, keys in RULE_KEYWORDS.items():
            if any(k in text for k in keys):
                return intent, 0.45
        return "reply", 0.25

    probs = model.predict_proba([text])[0]
    labels = model.classes_
    best_idx = int(np.argmax(probs))
    return labels[best_idx], float(probs[best_idx])

def active_learning_feedback(text: str, predicted_intent: str):
    speak("Was that correct? Say yes or no.")
    ans = listen_text().lower()
    if "no" in ans:
        speak("Okay, what did you mean? Say one of: open_app, close_app, search, time, read_file, write_file, reply, joke, exit.")
        correct = listen_text().strip()
        if correct:
            log_sample(text=text, intent=correct, confidence=1.0, source="corrected")
            speak("Thanks! I’ll learn from this next time.")

def allow_low_confidence(text, conf):
    short = len(text.split()) <= 2
    slangy = any(w in text.lower() for w in ["yo", "sup", "yar", "bhai"])
    noisy = sum(c.isalpha() for c in text) / max(1, len(text)) < 0.7

    if short or slangy or noisy:
        return conf >= 0.30
    return conf >= CONF_THRESHOLD

def _handle_single_command(command_text: str):
    """Handle one command after optional multi-command parsing."""
    if not command_text:
        return

    entities = extract_entities(command_text)
    intent, conf = predict_intent_with_confidence(command_text)

    # Explicit reminder phrasing gets reminder intent priority.
    if entities.get("reminder_time") and entities.get("reminder_message"):
        if any(k in command_text.lower() for k in ["remind me", "set reminder", "reminder"]):
            intent, conf = "reminder", 0.99

    print(f"🧠 Intent: {intent} (conf={conf:.2f})")

    if intent != "reminder" and not allow_low_confidence(command_text, conf):
        speak(f"I'm not sure what you mean by '{command_text}'. Try: open chrome, search python, write a note, tell me a joke, or time.")
        return

    if intent == "open_app":
        open_app_action(command_text)

    elif intent == "close_app":
        if not resolve_app(command_text):
            speak("Which app should I close?")
            return
        close_app_action(command_text)

    elif intent == "search":
        search_action(command_text)

    elif intent == "reminder":
        reminder_time = entities.get("reminder_time")
        reminder_message = entities.get("reminder_message")
        if not reminder_time or not reminder_message:
            speak("Please say reminder like: remind me at 7 pm to call mom.")
            return
        try:
            reminder = schedule_reminder(reminder_time, reminder_message)
            speak(f"Reminder set for {reminder_time}: {reminder['message']}")
        except ValueError as exc:
            speak(str(exc))

    elif intent == "time":
        time_action(command_text)

    elif intent == "joke":
        joke_action(command_text)

    elif intent == "write_file":
        write_file_action()

    elif intent == "read_file":
        read_file_action(command_text)

    elif intent == "reply":
        reply_action(command_text)

    elif intent == "exit":
        speak("Bye!")
        raise SystemExit

    else:
        speak("Sorry, I didn't understand.")

    if model is not None and AUTO_LEARN and conf >= AUTO_LEARN_MIN_CONF:
        log_sample(text=command_text, intent=intent, confidence=conf, source="auto")


def handle_text(text: str):
    if not text:
        return

    commands = split_commands(text)
    if not commands:
        return

    for command in commands:
        _handle_single_command(command)

    # Optional: active learning feedback
    # active_learning_feedback(text, intent)

if __name__ == "__main__":
    speak("hello")
    while True:
        try:
            text = listen_text()
            handle_text(text)
        except KeyboardInterrupt:
            speak("Exiting.")
            break
