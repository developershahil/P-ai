# 2–3 Minute Demo Script (Screen Recording)

This runbook is designed for a short product demo showing the existing Personal AI Assistant surfaces and reliability behaviors.

## 0) Pre-demo setup (before recording)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev,api]
cp .env.example .env
```

Optional (if you want API auth enabled in demo):

```bash
echo "API_KEY=demo-key" >> .env
```

## 1) Recording checklist (what must appear on screen)

- [ ] Terminal: CLI assistant accepting commands.
- [ ] Desktop window: PySide6 UI interaction and response rendering.
- [ ] Terminal: FastAPI running and successful `/ask` API call.
- [ ] Terminal: reminder exists before and after app/API restart (persistence).
- [ ] Terminal: fallback behavior with model unavailable (rule-based response still works).

---

## 2) Step-by-step demo flow (2–3 minutes)

### Step A — CLI usage (30–40s)

Run:

```bash
python -m personal_ai.main
```

Example inputs to type/say:

- `search python unit testing`
- `tell me a joke`

What to show:

- CLI accepts input and executes actions/replies.
- Intent/reply behavior visible in terminal logs/output.

> Stop the CLI with `Ctrl+C` after showing two quick interactions.

---

### Step B — Desktop UI interaction (25–35s)

Run:

```bash
python ui-desktop/main_window.py
```

Example input in UI text box:

- `search fastapi tutorial`

What to show:

- Chat interaction in desktop interface.
- Response/action feedback in the UI.

> Close the window once one interaction is demonstrated.

---

### Step C — FastAPI `/ask` call (25–35s)

Start API server:

```bash
uvicorn personal_ai.api.app:app --reload
```

In a second terminal, call `/ask`:

If API key is enabled:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-key" \
  -d '{"text":"search python dataclasses"}'
```

If API key is not enabled:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"text":"search python dataclasses"}'
```

What to show:

- JSON response from `/ask` including reply/command metadata.

---

### Step D — Reminder persistence across restart (35–45s)

With API still running, create a reminder:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-key" \
  -d '{"text":"set reminder at 7 pm to call mom"}'
```

Check reminders:

```bash
curl -H "x-api-key: demo-key" "http://127.0.0.1:8000/reminders"
```

Now restart API (`Ctrl+C`, then rerun uvicorn), and check again:

```bash
curl -H "x-api-key: demo-key" "http://127.0.0.1:8000/reminders"
```

What to show:

- Same reminder appears after restart (JSON persistence).

> If not using API key, omit the `x-api-key` header.

---

### Step E — Fallback when ML model is unavailable (20–30s)

In a terminal (stop API/CLI first), temporarily move model file:

```bash
mv personal_ai/models/intent_model.pkl personal_ai/models/intent_model.pkl.bak
python -m personal_ai.main
```

Enter:

- `search python decorators`

What to show:

- Assistant still handles the request via fallback rules (model missing warning may appear).

Restore model after demo:

```bash
mv personal_ai/models/intent_model.pkl.bak personal_ai/models/intent_model.pkl
```

---

## 3) Suggested recording structure (quick narration)

1. “CLI and desktop both use the same assistant core.”
2. “API exposes the same behavior via `/ask`.”
3. “Reminders persist across restarts.”
4. “If the ML model is unavailable, rule-based fallback still works.”
