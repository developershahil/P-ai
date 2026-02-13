"""Optional FastAPI app for future web UI integration."""

from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from personal_ai.core.assistant import MODE, handle_input, model
from personal_ai.reminders import list_reminders

app = FastAPI(title="Personal AI API", version="0.1.0")


class AskRequest(BaseModel):
    """Request payload for assistant text interactions."""

    text: str = Field(..., min_length=1, description="User message to process")


@app.post("/ask")
def ask(payload: AskRequest) -> Dict[str, Any]:
    """Process user text through the shared assistant backend."""
    return handle_input(payload.text)


@app.get("/status")
def status() -> Dict[str, Any]:
    """Return runtime mode and model availability."""
    return {"mode": MODE, "model_loaded": model is not None}


@app.get("/reminders")
def reminders() -> Dict[str, Any]:
    """Return reminder items persisted by the backend service."""
    return {"items": list_reminders()}
