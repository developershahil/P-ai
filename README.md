# Personal AI

[![CI](https://github.com/developershahil/P-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/developershahil/P-ai/actions/workflows/ci.yml)

Personal AI Assistant is a modular Python project with a shared assistant core exposed through:
- CLI (`python -m personal_ai.main`)
- Desktop UI (PySide6)
- FastAPI API (`/ask`, `/status`, `/reminders`)

## Release v1.0.0

**Highlights**
- Stable multi-interface runtime (CLI, desktop UI, API).
- Production-readiness updates: CI tests, structured logging, API key middleware, packaging script.
- ML lifecycle updates: retraining pipeline, metrics output, model version tracking.

## Demo

- Demo script: [`DEMO.md`](DEMO.md)
- Video/GIF: _Add demo link here_

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt && pip install -e .[dev,api]
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
curl -H "x-api-key: $API_KEY" http://127.0.0.1:8000/status
```

## Testing & CI

Run tests locally:

```bash
pytest -q
```

CI runs the same pytest suite on every push and pull request via GitHub Actions (`.github/workflows/ci.yml`).

## Packaging / Distribution

A PyInstaller build script is included:

```bash
python scripts/build_executable.py
```

This generates a standalone binary under `dist/`.

## Roadmap

(From `docs/ROADMAP.md`, current scope only)
- Improve model quality with existing intent + active-learning data.
- Continue tracking model metrics/version history across retraining cycles.
- Expand parser/entity/intent/reminder test coverage.
- Maintain API auth and structured logging hardening.
- Keep packaging reproducible with PyInstaller.

## Final QA Checklist

Pre-release QA and smoke-test plan: [`QA.md`](QA.md)

## Additional Docs

- `docs/ARCHITECTURE.md` – architecture overview
- `docs/DEVELOPMENT.md` – local dev workflow and CI
- `docs/IMPLEMENTATION_REFERENCE.md` – implementation status + logic notes
- `docs/ROADMAP.md` – scoped roadmap
