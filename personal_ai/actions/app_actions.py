import os, subprocess, webbrowser, datetime, random

from core.config import MODE
from security.permissions import load_permissions, save_permissions, is_blocked_exe



NOTES_FILE = "notes.txt"

APP_ALIASES = {
    "chrome": ["chrome", "google chrome", "browser", "my browser", "google", "chron", "chrome"],
    "notepad": ["notepad", "notes", "note"],
    "vscode": ["vs code", "vscode", "vs-code", "code editor", "code"],
    "youtube": ["youtube", "you tube", "youytube", "yt"],
    "explorer": ["file explorer", "explorer"]
}


KNOWN_APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "youtube": "https://www.youtube.com",
    "explorer": "explorer.exe",
}

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

def listen_text():
    if MODE == "local":
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as src:
                print("🎤 Listening...")
                audio = r.listen(src)
            return r.recognize_google(audio)
        except Exception:
            speak("Sorry, I didn't catch that.")
            return ""
    else:
        return input("You: ")

def resolve_app(text: str):
    t = text.lower()
    for app, aliases in APP_ALIASES.items():
        for a in aliases:
            if a in t:
                return app
    return None

def open_app_action(text: str):
    app = resolve_app(text)
    if not app:
        speak("Which app should I open?")
        return

    exe = os.path.expandvars(KNOWN_APPS.get(app))
    exe_name = os.path.basename(exe)
    if exe and exe_name and is_blocked_exe(exe_name):
        speak("This app is blocked for safety.")
        return

    perms = load_permissions()
    allowed = perms.get("allowed_apps", {})

    if app not in allowed:
        speak(f"Do you allow me to open {app} in future? Say yes or no.")
        if "yes" in listen_text().lower():
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
        if exe.startswith("http"):
            webbrowser.open(exe)
        else:
            subprocess.Popen(exe)
        speak(f"Opening {app}.")

def close_app_action(text: str):
    app = resolve_app(text)
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
    for w in ["search", "find", "look for", "google", "on youtube", "youtube"]:
        q = q.replace(w, "")
    q = q.strip()
    if not q:
        speak("What should I search for?")
        q = listen_text().strip()
        if not q:
            speak("Cancelled.")
            return

    if "youtube" in text.lower():
        url = f"https://www.youtube.com/results?search_query={q}"
    else:
        url = f"https://www.google.com/search?q={q}"

    if MODE == "dev":
        print(f"[DEV] Would open: {url}")
    else:
        webbrowser.open(url)

def time_action(text: str):
    now = datetime.datetime.now()
    if "date" in text.lower():
        speak(f"Today is {now.strftime('%A, %d %B %Y')}.")
    else:
        speak(f"It's {now.strftime('%I:%M %p')} right now.")

TECH_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why did the developer go broke? Because he used up all his cache."
]
GEN_JOKES = [
    "Why don’t scientists trust atoms? Because they make up everything!",
    "I tried to catch fog yesterday. Mist."
]
_last_joke = None

def joke_action(text: str):
    global _last_joke
    jokes = TECH_JOKES if "tech" in text.lower() else TECH_JOKES + GEN_JOKES
    joke = random.choice(jokes)
    while joke == _last_joke and len(jokes) > 1:
        joke = random.choice(jokes)
    _last_joke = joke
    speak(joke)

def write_file_action():
    speak("What should I write?")
    content = listen_text()
    if not content:
        speak("Nothing to save.")
        return

    speak("Append to notes or overwrite?")
    mode = listen_text().lower()
    write_mode = "a" if "append" in mode else "w"

    if write_mode == "w":
        speak("This will overwrite existing notes. Say yes to continue.")
        if "yes" not in listen_text().lower():
            speak("Cancelled.")
            return

    with open(NOTES_FILE, write_mode, encoding="utf-8") as f:
        f.write(content + "\n")
    speak("Saved.")

def read_file_action(text: str):
    if not os.path.exists(NOTES_FILE):
        speak("No notes found.")
        return

    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if "last" in text.lower():
        print("".join(lines[-3:]))
        speak("Here are the last notes.")
    elif "search" in text.lower():
        speak("What keyword should I search for?")
        kw = listen_text().lower()
        matches = [l for l in lines if kw in l.lower()]
        print("".join(matches) if matches else "No matches.")
        speak("Search complete.")
    else:
        print("".join(lines))
        speak("Here are your notes.")

def reply_action(_text: str):
    responses = [
        "Hi! How can I help you?",
        "Hello there! What would you like to do?",
        "Hey 🙂 What can I do for you?"
    ]
    speak(random.choice(responses))
