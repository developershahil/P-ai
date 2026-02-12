from pathlib import Path

from personal_ai.core.entities import extract_entities
from personal_ai.core.parser import split_commands
from personal_ai import reminders


def test_split_commands_basic():
    text = "open chrome and then search python then tell me a joke"
    assert split_commands(text) == [
        "open chrome",
        "search python",
        "tell me a joke",
    ]


def test_split_commands_preserves_reminder_message_phrase():
    text = "remind me at 7 pm to call mom and dad"
    assert split_commands(text) == ["remind me at 7 pm to call mom and dad"]


def test_extract_entities_no_false_app_match_from_python():
    entities = extract_entities("search python tutorials")
    assert entities["app"] is None
    assert entities["search_query"] == "python tutorials"


def test_extract_entities_reminder_fields():
    entities = extract_entities("set reminder at 19:00 to take medicine")
    assert entities["reminder_time"] == "19:00"
    assert entities["reminder_message"] == "take medicine"


def test_schedule_reminder_persists_to_json(tmp_path: Path):
    reminders.REMINDERS_FILE = tmp_path / "reminders.json"
    item = reminders.schedule_reminder("19:00", "call mom")

    stored = reminders._load_reminders()
    assert len(stored) == 1
    assert stored[0]["id"] == item["id"]
    assert stored[0]["message"] == "call mom"
    assert stored[0]["status"] == "pending"
