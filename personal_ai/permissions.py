import os, json

PERM_FILE = "app_permissions.json"
BLOCKED_EXES = {"cmd.exe", "powershell.exe", "regedit.exe", "wmic.exe"}

def load_permissions():
    if os.path.exists(PERM_FILE):
        with open(PERM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"allowed_apps": {}, "allowed_folders": []}

def save_permissions(perms):
    with open(PERM_FILE, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=2)

def is_blocked_exe(exe_name: str) -> bool:
    return exe_name.lower() in BLOCKED_EXES
