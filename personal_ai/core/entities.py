"""Entity extraction helpers for command routing."""

import re
from typing import Dict, Optional

from ..actions.app_actions import APP_ALIASES

_PLATFORM_ALIASES = {
    "youtube": ["youtube", "you tube", "yt"],
    "google": ["google", "web"],
}

# Matches:
# - remind me at 19:00 to call mom
# - set reminder at 7 pm to take medicine
# - reminder at 8:30am to join meeting
_REMINDER_RE = re.compile(
    r"(?:remind\s+me|set\s+reminder|reminder)\s+at\s+"
    r"(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+to\s+(?P<message>.+)$",
    flags=re.IGNORECASE,
)


def _has_alias(text: str, alias: str) -> bool:
    return re.search(rf"\b{re.escape(alias.lower())}\b", text.lower()) is not None


def _find_app_name(text: str) -> Optional[str]:
    for app, aliases in APP_ALIASES.items():
        if any(_has_alias(text, alias) for alias in aliases):
            return app
    return None


def _find_platform(text: str) -> Optional[str]:
    for platform, aliases in _PLATFORM_ALIASES.items():
        if any(_has_alias(text, alias) for alias in aliases):
            return platform
    return None


def _extract_search_query(text: str) -> Optional[str]:
    t = text.strip()

    patterns = [
        # "search python", "search python on youtube"
        r"(?:search|find|look up|look for|google)\s+(?:for\s+)?(.+?)(?:\s+on\s+youtube)?$",
        # "on youtube lo-fi music"
        r"on\s+youtube\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, t, flags=re.IGNORECASE)
        if match:
            query = match.group(1).strip(" .,")
            if query:
                return query

    return None


def extract_entities(text: str) -> Dict[str, Optional[str]]:
    """Extract key entities from a single command string.

    Returns a dictionary containing:
    - app: detected app name (e.g., chrome, vscode)
    - platform: detected platform for search (e.g., youtube)
    - search_query: text to search for
    - reminder_time: scheduled reminder time expression
    - reminder_message: reminder content
    """
    reminder_time = None
    reminder_message = None

    reminder_match = _REMINDER_RE.search(text.strip())
    if reminder_match:
        reminder_time = reminder_match.group("time").strip()
        reminder_message = reminder_match.group("message").strip()

    return {
        "app": _find_app_name(text),
        "platform": _find_platform(text),
        "search_query": _extract_search_query(text),
        "reminder_time": reminder_time,
        "reminder_message": reminder_message,
    }
