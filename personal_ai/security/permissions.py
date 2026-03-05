import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PERM_FILE = BASE_DIR / "app_permissions.json"
BLOCKED_EXES = {
    "cmd.exe",
    "powershell.exe",
    "powershell_ise.exe",
    "pwsh.exe",
    "regedit.exe",
    "wmic.exe",
}


def _default_permissions() -> dict:
    return {"allowed_apps": {}, "allowed_folders": []}


def load_permissions():
    if not PERM_FILE.exists():
        return _default_permissions()

    try:
        with PERM_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return _default_permissions()

    if not isinstance(data, dict):
        return _default_permissions()

    allowed_apps = data.get("allowed_apps")
    allowed_folders = data.get("allowed_folders")

    if not isinstance(allowed_apps, dict):
        allowed_apps = {}
    if not isinstance(allowed_folders, list):
        allowed_folders = []

    return {"allowed_apps": allowed_apps, "allowed_folders": allowed_folders}


def save_permissions(perms):
    with PERM_FILE.open("w", encoding="utf-8") as f:
        json.dump(perms, f, indent=2)


def is_blocked_exe(exe_name: str) -> bool:
    return exe_name.lower() in BLOCKED_EXES
