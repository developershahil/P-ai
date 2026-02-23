"""OpenAI-compatible provider for optional chat mode enhancement."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OpenAICompatibleProvider:
    """Small OpenAI-compatible chat completion client."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Chat mode will use fallback assistant behavior."
            )

    def generate(self, messages: list[dict[str, str]]) -> str:
        """Call the OpenAI-compatible chat completions endpoint."""
        payload = {
            "model": self.model,
            "messages": messages,
        }
        request = Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM request failed ({exc.code}): {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"LLM request failed: {exc.reason}") from exc

        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("LLM response missing choices.")

        content = choices[0].get("message", {}).get("content", "")
        text = content.strip()
        if not text:
            raise RuntimeError("LLM response content was empty.")
        return text

