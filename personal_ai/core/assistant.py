"""Core assistant orchestration for CLI, desktop UI, and API usage."""

import os
import random
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, List

joblib = None
np = None
if find_spec("joblib") is not None:
    import joblib  # type: ignore[assignment]
if find_spec("numpy") is not None:
    import numpy as np  # type: ignore[assignment]

from .config import MODE, CONF_THRESHOLD, AUTO_LEARN, AUTO_LEARN_MIN_CONF, SETTINGS
from .logging_config import get_logger
from .profile import load_profile, save_profile
from ..llm import OpenAICompatibleProvider
from ..llm.base import LLMProvider
from ..parser import split_commands
from ..entities import extract_entities
from ..actions.app_actions import resolve_app
from ..actions.app_actions import (
    open_app_action,
    close_app_action,
    open_path_action,
    close_path_action,
    search_action,
    time_action,
    joke_action,
    write_file_action,
    read_file_action,
    speak,
    listen_text,
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
logger = get_logger(__name__)
_NO_KEY_TIP_SHOWN = False


def _api_key_help_text() -> str:
    return (
        "API keys let chat mode use an online LLM for smarter replies.\\n\\n"
        "Set OPENAI_API_KEY and restart the app:\\n"
        "- Windows (PowerShell): setx OPENAI_API_KEY \"your_key_here\"\\n"
        "- Windows (CMD): set OPENAI_API_KEY=your_key_here\\n"
        "- Linux/macOS (bash/zsh): export OPENAI_API_KEY=\"your_key_here\""
    )


def _local_chat_reply() -> str:
    return random.choice(
        [
            "Hi! How can I help you?",
            "Hello there! What would you like to do?",
            "Hey 🙂 What can I do for you?",
        ]
    )


def _llm_chat_reply(text: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    if find_spec("openai") is None:
        logger.debug("openai_package_missing_falling_back_to_local_reply")
        return None

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            input=text,
        )
        content = getattr(response, "output_text", "").strip()
        return content or None
    except Exception as exc:  # noqa: BLE001
        logger.debug("llm_reply_failed_falling_back_to_local error=%s", exc)
        return None


def _chat_reply(text: str) -> str:
    global _NO_KEY_TIP_SHOWN

    llm_reply = _llm_chat_reply(text)
    if llm_reply:
        return llm_reply

    if not _NO_KEY_TIP_SHOWN and not os.getenv("OPENAI_API_KEY", "").strip():
        _NO_KEY_TIP_SHOWN = True
        return (
            "Tip: Add an API key to unlock smarter replies. Type 'help' to see how.\\n"
            f"{_local_chat_reply()}"
        )

    return _local_chat_reply()

CHAT_SYSTEM_PROMPT = (
    "You are Personal AI, a helpful and concise assistant. "
    "Give practical answers, keep context from recent messages, and be safe and polite."
)


def get_chat_provider() -> LLMProvider | None:
    """Return an LLM provider if configured, else None for fallback behavior."""
    try:
        return OpenAICompatibleProvider(
            api_key=SETTINGS.openai_api_key,
            model=SETTINGS.openai_model,
            base_url=SETTINGS.openai_base_url,
        )
    except RuntimeError as exc:
        print(f"ℹ️ Chat mode LLM disabled: {exc}")
        return None


def _as_chat_messages(history: list[dict[str, str]], user_text: str) -> list[dict[str, str]]:
    """Build a short ChatML-style payload for the provider."""
    turns = max(0, SETTINGS.chat_history_turns)
    trimmed = history[-(turns * 2) :] if turns else []
    return [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        *trimmed,
        {"role": "user", "content": user_text},
    ]


def handle_chat_input(text: str, history: list[dict[str, str]] | None = None) -> Dict[str, Any]:
    """Handle desktop chat mode with optional LLM and safe fallback."""
    history = history or []
    provider = get_chat_provider()
    if provider is None:
        print("ℹ️ Falling back to built-in assistant reply behavior.")
        return handle_input(text)

    messages = _as_chat_messages(history=history, user_text=text)
    try:
        reply = provider.generate(messages)
    except RuntimeError as exc:
        print(f"⚠️ LLM error, using fallback behavior: {exc}")
        return handle_input(text)

    return {
        "reply": reply,
        "commands": [{"input": text, "intent": "chat", "confidence": 1.0, "reply": reply, "actions": ["llm_chat"]}],
        "mode": MODE,
        "model_loaded": model is not None,
    }


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
        speak(
            "Okay, what did you mean? Say one of: open_app, close_app, search, time, read_file, write_file, reply, joke, exit."
        )
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


def _handle_single_command(command_text: str) -> Dict[str, Any]:
    """Handle one command and return structured metadata for UI/API consumers."""
    result: Dict[str, Any] = {
        "input": command_text,
        "intent": None,
        "confidence": 0.0,
        "reply": "",
        "actions": [],
    }
    if not command_text:
        result["reply"] = "No command received."
        return result

    if command_text.strip().lower() == "help":
        result["intent"] = "reply"
        result["confidence"] = 1.0
        result["actions"].append("chat_help")
        result["reply"] = _api_key_help_text()
        return result

    entities = extract_entities(command_text)
    intent, conf = predict_intent_with_confidence(command_text)

    # Explicit reminder phrasing gets reminder intent priority.
    if entities.get("reminder_time") and entities.get("reminder_message"):
        if any(k in command_text.lower() for k in ["remind me", "set reminder", "reminder"]):
            intent, conf = "reminder", 0.99

    result["intent"] = intent
    result["confidence"] = conf
    print(f"🧠 Intent: {intent} (conf={conf:.2f})")
    logger.info("intent_predicted input=%s intent=%s conf=%.3f", command_text, intent, conf)

    if intent != "reminder" and not allow_low_confidence(command_text, conf):
        result["reply"] = (
            f"I'm not sure what you mean by '{command_text}'. Try: open chrome, search python, "
            "write a note, tell me a joke, or time."
        )
        speak(result["reply"])
        return result

    path_terms = [" file", " folder", " directory", " document"]

    if intent == "open_app":
        if any(term in f" {command_text.lower()}" for term in path_terms):
            open_path_action(command_text)
            result["actions"].append("open_path_action")
            result["reply"] = "Attempted to open requested file or folder."
        else:
            open_app_action(command_text)
            result["actions"].append("open_app_action")
            result["reply"] = "Attempted to open requested application."

    elif intent == "close_app":
        if any(term in f" {command_text.lower()}" for term in path_terms):
            close_path_action(command_text)
            result["actions"].append("close_path_action")
            result["reply"] = "Attempted to close requested file or folder."
        else:
            if not resolve_app(command_text):
                result["reply"] = "Which app should I close?"
                speak(result["reply"])
                return result
            close_app_action(command_text)
            result["actions"].append("close_app_action")
            result["reply"] = "Attempted to close requested application."

    elif intent == "search":
        search_action(command_text)
        result["actions"].append("search_action")
        result["reply"] = "Search action triggered."

    elif intent == "reminder":
        reminder_time = entities.get("reminder_time")
        reminder_message = entities.get("reminder_message")
        if not reminder_time or not reminder_message:
            result["reply"] = "Please say reminder like: remind me at 7 pm to call mom."
            speak(result["reply"])
            return result
        try:
            reminder = schedule_reminder(reminder_time, reminder_message)
            result["actions"].append("schedule_reminder")
            result["reply"] = f"Reminder set for {reminder_time}: {reminder['message']}"
            speak(result["reply"])
        except ValueError as exc:
            result["reply"] = str(exc)
            speak(result["reply"])

    elif intent == "time":
        time_action(command_text)
        result["actions"].append("time_action")
        result["reply"] = "Shared current time/date."

    elif intent == "joke":
        joke_action(command_text)
        result["actions"].append("joke_action")
        result["reply"] = "Told a joke."

    elif intent == "write_file":
        write_file_action()
        result["actions"].append("write_file_action")
        result["reply"] = "Write-note flow started."

    elif intent == "read_file":
        read_file_action(command_text)
        result["actions"].append("read_file_action")
        result["reply"] = "Read-note flow started."

    elif intent == "reply":
        chat_reply = _chat_reply(command_text)
        speak(chat_reply)
        result["actions"].append("reply_action")
        result["reply"] = chat_reply

    elif intent == "exit":
        result["reply"] = "Bye!"
        speak(result["reply"])
        raise SystemExit

    else:
        result["reply"] = "Sorry, I didn't understand."
        speak(result["reply"])

    if model is not None and AUTO_LEARN and conf >= AUTO_LEARN_MIN_CONF:
        log_sample(text=command_text, intent=intent, confidence=conf, source="auto")

    profile = load_profile()
    profile["last_intent"] = intent
    save_profile(profile)

    return result


def handle_input(text: str) -> Dict[str, Any]:
    """Process text input and return structured response without changing CLI behavior."""
    if not text:
        logger.error("empty_input_received")
        return {"reply": "Please type something.", "commands": [], "mode": MODE, "model_loaded": model is not None}

    commands = split_commands(text)
    if not commands:
        return {"reply": "I could not detect a command.", "commands": [], "mode": MODE, "model_loaded": model is not None}

    command_results: List[Dict[str, Any]] = []
    for command in commands:
        command_results.append(_handle_single_command(command))

    final_reply = command_results[-1].get("reply", "Done.") if command_results else "Done."
    return {
        "reply": final_reply,
        "commands": command_results,
        "mode": MODE,
        "model_loaded": model is not None,
    }


def handle_text(text: str):
    """Backward-compatible CLI helper that performs side-effects only."""
    if not text:
        return
    handle_input(text)


if __name__ == "__main__":
    speak("hello")
    while True:
        try:
            text = listen_text()
            handle_text(text)
        except KeyboardInterrupt:
            speak("Exiting.")
            break
