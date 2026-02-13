"""Command parsing utilities for splitting multi-intent user input."""

import re
from typing import List

_COMMAND_STARTERS = [
    "open", "launch", "start", "close", "quit", "stop",
    "search", "find", "look", "google",
    "read", "write", "save", "create",
    "tell", "say", "what", "show",
    "remind", "set", "exit", "bye",
]
_STARTER_PATTERN = "|".join(_COMMAND_STARTERS)
_COMMAND_SPLIT_RE = re.compile(
    rf"\s+(?:and then|then|and)\s+(?=(?:{_STARTER_PATTERN})\b)",
    flags=re.IGNORECASE,
)


def split_commands(text: str) -> List[str]:
    """Split a user utterance into individual command strings."""
    if not text:
        return []

    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []

    parts = [p.strip(" ,.;") for p in _COMMAND_SPLIT_RE.split(normalized)]
    return [p for p in parts if p]
