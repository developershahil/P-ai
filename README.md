# Personal AI

[![CI](https://github.com/developershahil/P-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/developershahil/P-ai/actions/workflows/ci.yml)

A modular Python personal assistant platform with:

- **Backend package** (`personal_ai/`) for assistant logic.
- **Desktop UI** (`ui-desktop/`) powered by PySide6.
- **Optional FastAPI layer** (`personal_ai/api/`) for integrations.
- **Future web UI placeholder** (`ui-web/`) for planned React frontend work.

## Release v1.0.0

**Highlights**
- Stable multi-interface assistant runtime (CLI, desktop PySide6 UI, and FastAPI API).
- Production-readiness updates: CI test workflow, expanded unit tests, structured logging, API key protection, and PyInstaller packaging script.
- ML lifecycle updates: retraining pipeline, evaluation metrics (accuracy/F1/confusion matrix), and model version tracking.

## Platform Support

- Linux: CI validated
- Windows: CI validated
- macOS: manual test recommended

## Repository structure

```text
.
├── personal_ai/              # Backend package + CLI + optional API
├── ui-desktop/               # PySide6 desktop application
├── ui-web/                   # Placeholder for future web UI (docs only)
├── docs/                     # Architecture and setup docs
├── tests/                    # Pytest suite
├── scripts/                  # Utility scripts (retrain/build)
├── pyproject.toml            # Packaging and tool config
├── requirements.txt          # Runtime dependencies
└── README.md
```

## Demo

- Demo script: [`DEMO.md`](DEMO.md)
- Video/GIF: _Add demo link here_

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev]
cp .env.example .env
```

## Windows Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .[dev]
copy .env.example .env
```

## Windows one-command test + run

Use this PowerShell helper to validate text flow, optional voice dependencies, and security guardrails before launching:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_test_and_run.ps1
```

Optional launch flags:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_test_and_run.ps1 -StartCli
powershell -ExecutionPolicy Bypass -File .\scripts\windows_test_and_run.ps1 -StartDesktop
```

## Run the assistant

```bash
python -m personal_ai.main
```

## Run desktop UI

```bash
python ui-desktop/main_window.py
```

## ChatGPT-like chat mode (optional)

Desktop chat mode can use a Groq or OpenAI-compatible LLM for smarter replies.

1. Set an API key in your environment (Groq preferred):
   - **Windows (PowerShell):** `$env:GROQ_API_KEY="your_key_here"`
   - **macOS/Linux:** `export GROQ_API_KEY="your_key_here"`
2. (Optional) Override endpoint/model:
   - `GROQ_BASE_URL` (default: `https://api.groq.com/openai/v1`)
   - `GROQ_MODEL` (default: `llama-3.1-8b-instant`)
3. Optional OpenAI fallback variables:
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)
   - `OPENAI_MODEL` (default: `gpt-4o-mini`)
4. Start desktop UI: `python ui-desktop/main_window.py`

If no LLM key is set, chat mode automatically falls back to existing assistant behavior and prints a clear console message. Non-chat features continue to work without Groq/OpenAI.

## Run optional API

```bash
pip install -e .[api]
uvicorn personal_ai.api.app:app --reload
```

## Security model

- **Blocked executables:** high-risk binaries are blocked (`cmd.exe`, `powershell.exe`, `regedit.exe`, `wmic.exe`).
- **Allow-list permissions:** app/folder permissions are persisted in `personal_ai/app_permissions.json` as `allowed_apps` and `allowed_folders`.
- **File/folder voice control:** say commands like `open file "C:\Users\you\Documents\todo.txt"` or `open folder Projects`; first-time folder access is saved in `allowed_folders`.
- **API key auth:** when `API_KEY` is set in `.env`, API requests must include `x-api-key`.

API key example:

```bash
curl -H "x-api-key: $API_KEY" http://127.0.0.1:8000/status
```

## ML retraining and evaluation

Run the retraining pipeline:

```bash
python scripts/retrain_model.py
```

Optional: write machine-readable retraining output for automation:

```bash
python scripts/retrain_model.py --json-output retrain_result.json
```

Training writes/updates:

- `personal_ai/models/model_metrics.json` (accuracy, macro F1, confusion matrix)
- `personal_ai/models/model_version.json` (model version tracking)

### Automatic retraining (GitHub Actions)

This repository includes `.github/workflows/retrain.yml` which runs retraining automatically every Monday at 03:00 UTC (and can be run manually through `workflow_dispatch`).

Safety behavior:

- Promotion only occurs when candidate accuracy or macro-F1 exceeds the current model by `MODEL_IMPROVEMENT_THRESHOLD`.
- If promoted, workflow commits and pushes:
  - `personal_ai/models/intent_model.pkl`
  - `personal_ai/models/model_metrics.json`
  - `personal_ai/models/model_version.json`
- If not promoted, no commit is created.

The workflow always uploads retraining artifacts (`retrain_result.json` and metrics/version files when available) for auditability.

## Build standalone executable (PyInstaller)

```bash
python scripts/build_executable.py
```

Output binary is created under `dist/`.

### Windows build and run

```powershell
python scripts/build_executable.py
.\dist\personal-ai.exe
```

## Testing & CI

Run tests locally:

```bash
pytest -q
```

CI runs the same pytest suite on every push and pull request via GitHub Actions (`.github/workflows/ci.yml`).

## Additional docs

- `docs/ARCHITECTURE.md` – architecture overview
- `docs/DEVELOPMENT.md` – local dev workflow and CI
- `docs/IMPLEMENTATION_REFERENCE.md` – implementation status + logic notes
- `docs/ROADMAP.md` – focused roadmap
- `QA.md` – pre-release QA and smoke-test plan
