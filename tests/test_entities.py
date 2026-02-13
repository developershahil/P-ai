"""Tests for entity extraction utilities."""

from personal_ai.entities import extract_entities


def test_extract_entities_no_false_app_match_from_python() -> None:
    entities = extract_entities("search python tutorials")
    assert entities["app"] is None
    assert entities["search_query"] == "python tutorials"


def test_extract_entities_reminder_fields() -> None:
    entities = extract_entities("set reminder at 19:00 to take medicine")
    assert entities["reminder_time"] == "19:00"
    assert entities["reminder_message"] == "take medicine"
