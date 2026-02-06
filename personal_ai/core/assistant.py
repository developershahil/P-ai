import joblib
import numpy as np

from core.config import MODE, CONF_THRESHOLD
from actions.app_actions import resolve_app
from actions.app_actions import (
    open_app_action, close_app_action, search_action,
    time_action, joke_action, write_file_action, read_file_action,
    reply_action, speak, listen_text
)


print(f"🔧 Running in {MODE.upper()} mode")

MODEL_PATH = "intent_model.pkl"
model = joblib.load(MODEL_PATH)

def predict_intent_with_confidence(text: str):
    probs = model.predict_proba([text.lower()])[0]
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
            with open("intents.csv", "a", encoding="utf-8") as f:
                f.write(f"\n{text},{correct}")
            speak("Thanks! I’ll learn from this next time.")

def allow_low_confidence(text, conf):
    short = len(text.split()) <= 2
    slangy = any(w in text.lower() for w in ["yo", "sup", "yar", "bhai"])
    noisy = sum(c.isalpha() for c in text) / max(1, len(text)) < 0.7

    if short or slangy or noisy:
        return conf >= 0.30
    return conf >= CONF_THRESHOLD

def handle_text(text: str):
    if not text:
        return

    intent, conf = predict_intent_with_confidence(text)
    print(f"🧠 Intent: {intent} (conf={conf:.2f})")

    if not allow_low_confidence(text, conf):
        speak(f"I'm not sure what you mean by '{text}'. Try: open chrome, search python, write a note, tell me a joke, or time.")
        return

    if intent == "open_app":
        open_app_action(text)

    elif intent == "close_app":
        if not resolve_app(text):
            speak("Which app should I close?")
            return
        close_app_action(text)

    elif intent == "search":
        search_action(text)

    elif intent == "time":
        time_action(text)

    elif intent == "joke":
        joke_action(text)

    elif intent == "write_file":
        write_file_action()

    elif intent == "read_file":
        read_file_action(text)

    elif intent == "reply":
        reply_action(text)

    elif intent == "exit":
        speak("Bye!")
        raise SystemExit

    else:
        speak("Sorry, I didn't understand.")

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
