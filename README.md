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

For architecture details, see `docs/ARCHITECTURE.md`.

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

## Run the CLI assistant

```bash
python -m personal_ai.main
python ui-desktop/main_window.py
uvicorn personal_ai.api.app:app --reload
```

## Security Model

- **Blocked executables:** high-risk binaries are blocked (`cmd.exe`, `powershell.exe`, `regedit.exe`, `wmic.exe`).
- **Allow-list permissions:** app/folder permissions are persisted in `personal_ai/app_permissions.json` as `allowed_apps` and `allowed_folders`.
- **API key auth:** when `API_KEY` is set (for example in `.env`), API requests must include `x-api-key`.

Example API auth check:

```bash
uvicorn personal_ai.api.app:app --reload
```

### API endpoints

- `POST /ask`
- `GET /status`
- `GET /reminders`

### API key auth

If `API_KEY` is set in `.env`, all API endpoints require request header `x-api-key`.

```bash
curl -H "x-api-key: $API_KEY" http://127.0.0.1:8000/status
```

## ML retraining and evaluation

Run the retraining pipeline:

```bash
python scripts/retrain_model.py
```

Training writes/updates:

- `personal_ai/models/model_metrics.json` (accuracy, macro F1, confusion matrix)
- `personal_ai/models/model_version.json` (model version tracking)

## Build standalone executable (PyInstaller)

```bash
pip install -e .[dev]
python scripts/build_executable.py
```

Output binary is created under `dist/`.

## Testing & CI

Run tests locally:

```bash
pytest -q
```

## Additional docs

- `docs/DEVELOPMENT.md` – local dev workflow and CI
- `docs/ROADMAP.md` – focused roadmap
- `docs/IMPLEMENTATION_REFERENCE.md` – implementation status + logic notes
