"""Tests for parser behavior and multi-command splitting."""

from personal_ai.parser import split_commands


def test_split_commands_basic() -> None:
    text = "open chrome and then search python then tell me a joke"
    assert split_commands(text) == ["open chrome", "search python", "tell me a joke"]


def test_split_commands_preserves_reminder_message_phrase() -> None:
    text = "remind me at 7 pm to call mom and dad"
    assert split_commands(text) == ["remind me at 7 pm to call mom and dad"]
