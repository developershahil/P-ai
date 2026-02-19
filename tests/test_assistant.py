"""Unit tests for assistant intent handling."""

from personal_ai.core import assistant


def test_handle_input_search_intent(monkeypatch):
    monkeypatch.setattr(assistant, "predict_intent_with_confidence", lambda _text: ("search", 0.95))
    monkeypatch.setattr(assistant, "search_action", lambda _text: None)
    monkeypatch.setattr(assistant, "load_profile", lambda: {"user_name": "", "preferred_mode": "", "last_intent": ""})
    monkeypatch.setattr(assistant, "save_profile", lambda _profile: None)

    result = assistant.handle_input("search python testing")

    assert result["commands"][0]["intent"] == "search"
    assert "search_action" in result["commands"][0]["actions"]


def test_handle_input_empty_text_returns_prompt():
    result = assistant.handle_input("")
    assert result["reply"] == "Please type something."
    assert result["commands"] == []
