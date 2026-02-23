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


def test_handle_chat_input_uses_provider(monkeypatch):
    captured = {}

    class FakeProvider:
        def generate(self, messages):
            captured["messages"] = messages
            return "LLM reply"

    monkeypatch.setattr(assistant, "get_chat_provider", lambda: FakeProvider())

    history = [{"role": "assistant", "content": "Hello"}]
    result = assistant.handle_chat_input("How are you?", history=history)

    assert result["reply"] == "LLM reply"
    assert result["commands"][0]["intent"] == "chat"
    assert captured["messages"][0]["role"] == "system"
    assert captured["messages"][-1] == {"role": "user", "content": "How are you?"}


def test_handle_chat_input_falls_back_without_provider(monkeypatch):
    fallback_payload = {"reply": "fallback", "commands": [], "mode": "dev", "model_loaded": False}
    monkeypatch.setattr(assistant, "get_chat_provider", lambda: None)
    monkeypatch.setattr(assistant, "handle_input", lambda _text: fallback_payload)

    result = assistant.handle_chat_input("hello")

    assert result == fallback_payload


def test_chat_reply_without_openai_api_key_uses_local_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(assistant, "_NO_KEY_TIP_SHOWN", False)
    monkeypatch.setattr(assistant, "predict_intent_with_confidence", lambda _text: ("reply", 0.95))
    monkeypatch.setattr(assistant, "load_profile", lambda: {"user_name": "", "preferred_mode": "", "last_intent": ""})
    monkeypatch.setattr(assistant, "save_profile", lambda _profile: None)
    monkeypatch.setattr(assistant, "speak", lambda _text: None)

    result = assistant.handle_input("hello")

    assert "Tip: Add an API key to unlock smarter replies." in result["reply"]
    assert result["commands"][0]["intent"] == "reply"


def test_help_command_returns_api_key_setup_instructions():
    result = assistant.handle_input("help")

    assert "PowerShell" in result["reply"]
    assert "setx OPENAI_API_KEY \"your_key_here\"" in result["reply"]
    assert "set OPENAI_API_KEY=your_key_here" in result["reply"]
    assert "export OPENAI_API_KEY=\"your_key_here\"" in result["reply"]
