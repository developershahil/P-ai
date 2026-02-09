# hard_tester_v2.py
from pathlib import Path

import joblib
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "intent_model.pkl"
model = joblib.load(MODEL_PATH)

def predict_intent_with_confidence(text: str):
    probs = model.predict_proba([text.lower()])[0]
    labels = model.classes_
    best_idx = int(np.argmax(probs))
    return labels[best_idx], float(probs[best_idx])

HARD_TEST_CASES = [
    # Slang + greetings
    ("yo", "reply"),
    ("sup", "reply"),
    ("hello bhai", "reply"),
    ("hey yaar", "reply"),

    # Polite + long open app
    ("could you please open my browser for me", "open_app"),
    ("can you start vs code right now", "open_app"),
    ("i want you to open chrome asap", "open_app"),
    ("pls launch youtube app", "open_app"),

    # Indirect close app
    ("i am done with chrome, close it", "close_app"),
    ("this browser is annoying, quit it", "close_app"),
    ("can you stop youtube now", "close_app"),

    # Messy search requests
    ("umm can you maybe search best python scraping libs", "search"),
    ("bro find me dotnet fresher jobs near rajkot", "search"),
    ("hey google sql joins example", "search"),
    ("look something up about entity framework", "search"),

    # Time/date with noise
    ("bro what's the time right now", "time"),
    ("tell me today's date please yaar", "time"),
    ("what day is it today actually", "time"),

    # Typos extreme
    ("opn chorme", "open_app"),
    ("cls crome", "close_app"),
    ("serch pythn", "search"),
    ("wat tym", "time"),
    ("jok", "joke"),

    # Notes with indirect phrasing
    ("make a note of this please", "write_file"),
    ("can you save this message for me", "write_file"),
    ("show me whatever i wrote earlier", "read_file"),
    ("read out my notes", "read_file"),

    # Mixed intents (expect primary)
    ("open chrome and search python tutorials", "open_app"),
    ("close youtube and tell me a joke", "close_app"),
    ("search sql joins then open vs code", "search"),

    # Exit assistant (indirect)
    ("i think i'm done here", "exit"),
    ("you can stop now", "exit"),
    ("let's end this", "exit"),

    # Ambiguous
    ("open", "open_app"),
    ("close", "close_app"),
    ("search something", "search"),
    ("do something", "reply"),
]

def run_hard_tests():
    passed = 0
    for text, expected in HARD_TEST_CASES:
        pred, conf = predict_intent_with_confidence(text)
        ok = "✅ PASS" if pred == expected else "❌ FAIL"
        print(f"{ok} | '{text}' → {pred} (conf={conf:.2f}), expected={expected}")
        if pred == expected:
            passed += 1

    total = len(HARD_TEST_CASES)
    acc = passed / total * 100
    print(f"\n🔥 Boss-level Accuracy: {passed}/{total} = {acc:.1f}%")

if __name__ == "__main__":
    run_hard_tests()
