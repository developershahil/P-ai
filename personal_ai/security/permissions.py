import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PERM_FILE = BASE_DIR / "app_permissions.json"
BLOCKED_EXES = {"cmd.exe", "powershell.exe", "regedit.exe", "wmic.exe"}

def load_permissions():
    if PERM_FILE.exists():
        with PERM_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"allowed_apps": {}, "allowed_folders": []}

def save_permissions(perms):
    with PERM_FILE.open("w", encoding="utf-8") as f:
        json.dump(perms, f, indent=2)

def is_blocked_exe(exe_name: str) -> bool:
    return exe_name.lower() in BLOCKED_EXES
