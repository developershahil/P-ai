# Final QA Checklist & Smoke Test Plan

Use this checklist before tagging/releasing.

## 1) Fresh setup on a new machine

- [ ] Clone repository and open project root.
- [ ] Create virtual environment and install dependencies.
- [ ] Copy environment template.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev,api]
cp .env.example .env
```

## 2) CLI smoke test

Run:

```bash
python -m personal_ai.main
```

Checks:
- [ ] Assistant starts without crash.
- [ ] Basic command works (example: `search python testing`).
- [ ] Graceful exit with `Ctrl+C`.

## 3) Desktop UI responsiveness (no freeze)

Run:

```bash
python ui-desktop/main_window.py
```

Checks:
- [ ] Window opens successfully.
- [ ] Send at least one command from UI (example: `search fastapi docs`).
- [ ] UI remains responsive while processing (no freezing/hang).
- [ ] Window closes cleanly.

## 4) API auth check (blocked without key, allowed with key)

Set API key in `.env`:

```bash
echo "API_KEY=qa-demo-key" >> .env
uvicorn personal_ai.api.app:app --reload
```

In another terminal:

Blocked without key (expect 401):

```bash
curl -i http://127.0.0.1:8000/status
```

Allowed with key (expect 200):

```bash
curl -i -H "x-api-key: qa-demo-key" http://127.0.0.1:8000/status
```

Checks:
- [ ] Request without `x-api-key` is rejected.
- [ ] Request with correct `x-api-key` succeeds.

## 5) Reminder persistence after restart

Create reminder via API:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -H "x-api-key: qa-demo-key" \
  -d '{"text":"set reminder at 7 pm to call mom"}'
```

Read reminders:

```bash
curl -H "x-api-key: qa-demo-key" "http://127.0.0.1:8000/reminders"
```

Restart API server, then read reminders again.

Checks:
- [ ] Reminder exists before restart.
- [ ] Same reminder is still present after restart.

## 6) ML fallback when model is missing

Temporarily move model file:

```bash
mv personal_ai/models/intent_model.pkl personal_ai/models/intent_model.pkl.bak
python -m personal_ai.main
```

Try a known rule-based command:
- `search python decorators`

Restore model:

```bash
mv personal_ai/models/intent_model.pkl.bak personal_ai/models/intent_model.pkl
```

Checks:
- [ ] Assistant runs without model file.
- [ ] Rule-based fallback still handles command.

## 7) Logging files are created

After running CLI/API interactions, verify log files:

```bash
ls personal_ai/logs
```

Checks:
- [ ] `app.log` exists.
- [ ] `error.log` exists (after at least one error condition, if applicable).

## 8) Packaging build smoke test (if packaging is enabled)

Run:

```bash
python scripts/build_executable.py
```

Checks:
- [ ] PyInstaller build completes successfully.
- [ ] Output artifact exists under `dist/`.

## 9) Optional quick regression

```bash
pytest -q
```

Checks:
- [ ] Unit tests pass.
