"""Shared interface for optional LLM providers."""

from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    """Provider contract for chat-completion style text generation."""

    def generate(self, messages: list[dict[str, str]]) -> str:
        """Generate an assistant reply from role-based messages."""

