"""Persistent reminder scheduling with a background checker thread."""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
REMINDERS_FILE = BASE_DIR / "data" / "reminders.json"

_CHECK_INTERVAL_SECONDS = 20

_lock = threading.Lock()
_worker_started = False


def _load_reminders() -> List[Dict[str, str]]:
    if not REMINDERS_FILE.exists():
        return []
    try:
        with REMINDERS_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload
    except Exception:
        return []
    return []


def _save_reminders(reminders: List[Dict[str, str]]) -> None:
    REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REMINDERS_FILE.open("w", encoding="utf-8") as handle:
        json.dump(reminders, handle, indent=2)


def _parse_reminder_time(raw_time: str) -> Optional[datetime]:
    cleaned = " ".join(raw_time.strip().lower().split())
    now = datetime.now()

    formats = ["%H:%M", "%I %p", "%I:%M %p"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            scheduled = now.replace(
                hour=parsed.hour,
                minute=parsed.minute,
                second=0,
                microsecond=0,
            )
            if scheduled <= now:
                scheduled += timedelta(days=1)
            return scheduled
        except ValueError:
            continue

    return None


def schedule_reminder(time_text: str, message: str) -> Dict[str, str]:
    """Schedule a reminder and persist it to disk.

    Raises:
        ValueError: if the provided time format is not supported.
    """
    scheduled_dt = _parse_reminder_time(time_text)
    if scheduled_dt is None:
        raise ValueError("Invalid reminder time format. Use HH:MM or 7 pm / 7:30 pm.")

    reminder = {
        "id": f"r-{int(time.time() * 1000)}",
        "message": message.strip(),
        "scheduled_for": scheduled_dt.isoformat(),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    with _lock:
        reminders = _load_reminders()
        reminders.append(reminder)
        _save_reminders(reminders)

    return reminder


def _run_checker_loop() -> None:
    while True:
        now = datetime.now()
        with _lock:
            reminders = _load_reminders()
            changed = False
            for reminder in reminders:
                if reminder.get("status") != "pending":
                    continue
                when = reminder.get("scheduled_for")
                if not when:
                    continue
                try:
                    due = datetime.fromisoformat(when)
                except ValueError:
                    continue

                if due <= now:
                    print(f"⏰ Reminder: {reminder.get('message', 'No message')}")
                    reminder["status"] = "done"
                    reminder["triggered_at"] = now.isoformat()
                    changed = True

            if changed:
                _save_reminders(reminders)

        time.sleep(_CHECK_INTERVAL_SECONDS)


def start_reminder_service() -> None:
    """Start the background reminder checker once per process."""
    global _worker_started
    if _worker_started:
        return

    thread = threading.Thread(target=_run_checker_loop, name="reminder-checker", daemon=True)
    thread.start()
    _worker_started = True
