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

## Run the assistant

```bash
python -m personal_ai.main
```

## Run desktop UI

```bash
python ui-desktop/main_window.py
```

## Run optional API

```bash
pip install -e .[api]
uvicorn personal_ai.api.app:app --reload
```

## Security model

- **Blocked executables:** high-risk binaries are blocked (`cmd.exe`, `powershell.exe`, `regedit.exe`, `wmic.exe`).
- **Allow-list permissions:** app/folder permissions are persisted in `personal_ai/app_permissions.json` as `allowed_apps` and `allowed_folders`.
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

Training writes/updates:

- `personal_ai/models/model_metrics.json` (accuracy, macro F1, confusion matrix)
- `personal_ai/models/model_version.json` (model version tracking)

## Build standalone executable (PyInstaller)

```bash
python scripts/build_executable.py
```

Output binary is created under `dist/`.

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
