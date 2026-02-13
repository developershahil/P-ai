"""Tests for reminder persistence and scheduling."""

from pathlib import Path

import personal_ai.reminders.service as reminder_service


def test_schedule_reminder_persists_to_json(tmp_path: Path) -> None:
    reminder_service.REMINDERS_FILE = tmp_path / "reminders.json"
    item = reminder_service.schedule_reminder("19:00", "call mom")

    stored = reminder_service._load_reminders()
    assert len(stored) == 1
    assert stored[0]["id"] == item["id"]
    assert stored[0]["message"] == "call mom"
    assert stored[0]["status"] == "pending"
