import os
import json
import subprocess
import webbrowser
import datetime
import random
import joblib

# ---------- MODE (auto-detect with manual override) ----------
def detect_mode():
    try:
        import speech_recognition  # noqa
        import pyttsx3  # noqa
        return "local"
    except Exception:
        return "dev"

MODE = os.getenv("MODE") or detect_mode()
print(f"🔧 Running in {MODE.upper()} mode")

# ---------- CONFIG ----------
MODEL_PATH = "intent_model.pkl"
PERM_FILE = "app_permissions.json"
NOTES_FILE = "notes.txt"

BLOCKED_EXES = {"cmd.exe", "powershell.exe", "regedit.exe", "wmic.exe"}

# Update these paths on your Windows machine if needed
KNOWN_APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "explorer": "explorer.exe",
}

# ---------- ML ----------
model = joblib.load(MODEL_PATH)

def predict_intent(text: str) -> str:
    return model.predict([text.lower()])[0]

# ---------- IO (Voice/Text) ----------
def speak(text: str):
    if MODE == "local":
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            print(text)
    else:
        print(text)

def listen_text() -> str:
    if MODE == "local":
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("🎤 Listening...")
                audio = r.listen(source)
            return r.recognize_google(audio)
        except Exception:
            speak("Sorry, I didn't catch that. Please repeat.")
            return ""
    else:
        return input("You: ")

# ---------- PERMISSIONS ----------
def load_permissions():
    if os.path.exists(PERM_FILE):
        with open(PERM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"allowed_apps": {}}

def save_permissions(perms):
    with open(PERM_FILE, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=2)

# ---------- ENTITY EXTRACTION ----------
def extract_app_name(text: str):
    t = text.lower()
    for name in KNOWN_APPS.keys():
        if name in t.replace(" ", "") or name in t:
            return name
    return None

# ---------- ACTIONS ----------
def open_app_action(text: str):
    app = extract_app_name(text)
    if not app:
        speak("Which app should I open?")
        return

    exe = os.path.expandvars(KNOWN_APPS.get(app))
    exe_name = os.path.basename(exe).lower()
    if exe_name in BLOCKED_EXES:
        speak("This application is blocked for safety.")
        return

    perms = load_permissions()
    allowed = perms.get("allowed_apps", {})

    if app not in allowed:
        speak(f"Do you allow me to open {app} in future? Say yes or no.")
        ans = listen_text().lower()
        if "yes" in ans:
            allowed[app] = exe
            perms["allowed_apps"] = allowed
            save_permissions(perms)
            speak("Permission saved.")
        else:
            speak("Okay, not opening it.")
            return

    if MODE == "dev":
        print(f"[DEV] Would open: {exe}")
    else:
        subprocess.Popen(exe)
        speak(f"Opening {app}.")

def close_app_action(text: str):
    app = extract_app_name(text)
    if not app:
        speak("Which app should I close?")
        return

    perms = load_permissions()
    allowed = perms.get("allowed_apps", {})
    if app not in allowed:
        speak("This app is not approved to close.")
        return

    exe = os.path.basename(allowed[app])
    if MODE == "dev":
        print(f"[DEV] Would close: {exe}")
    else:
        os.system(f"taskkill /f /im {exe}")
        speak(f"Closed {app}.")

def search_action(text: str):
    q = text.lower()
    for w in ["search", "find", "look for", "google"]:
        q = q.replace(w, "")
    url = f"https://www.google.com/search?q={q.strip()}"
    if MODE == "dev":
        print(f"[DEV] Would open: {url}")
    else:
        webbrowser.open(url)

def time_action():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"The time is {now}")

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break, and it said: no problem, I’ll go to sleep.",
    "Why did the developer go broke? Because he used up all his cache."
]

def joke_action():
    speak(random.choice(JOKES))

def write_file_action():
    speak("What should I write?")
    text = listen_text()
    if not text:
        speak("Nothing to save.")
        return
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    speak("Saved to notes.")

def read_file_action():
    if not os.path.exists(NOTES_FILE):
        speak("No notes found.")
        return
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    speak("Here are your notes.")
    print(content)

# ---------- ROUTER ----------
def handle_text(text: str):
    if not text:
        return
    intent = predict_intent(text)
    print(f"🧠 Intent: {intent}")

    if intent == "open_app":
        open_app_action(text)
    elif intent == "close_app":
        close_app_action(text)
    elif intent == "search":
        search_action(text)
    elif intent == "time":
        time_action()
    elif intent == "joke":
        joke_action()
    elif intent == "write_file":
        write_file_action()
    elif intent == "read_file":
        read_file_action()
    elif intent == "exit":
        speak("Bye!")
        raise SystemExit
    else:
        speak("Sorry, I didn't understand.")

# ---------- MAIN ----------
if __name__ == "__main__":
    speak("hello, nice to meet you.")
    while True:
        try:
            text = listen_text()
            handle_text(text)
        except KeyboardInterrupt:
            speak("Exiting.")
            break
