# Architecture Overview

This repository is organized as a layered Personal AI platform with clear boundaries between backend logic, desktop UI, and future web capabilities.

## Layers

### 1) Backend package: `personal_ai/`

- Contains core assistant orchestration, parser/entity logic, reminders, actions, ML, and CLI entrypoints.
- `personal_ai/main.py` remains the CLI application entrypoint.
- `personal_ai/core/assistant.py` now provides:
  - `handle_text(text)`: backward-compatible CLI side-effect flow.
  - `handle_input(text)`: structured response API suitable for UI/API consumers.

### 2) Desktop UI: `ui-desktop/`

- PySide6-based desktop client is isolated from backend internals.
- Uses only backend public behavior (`handle_input`) and displays:
  - chat transcript
  - confidence score
  - action logs
  - runtime status bar
- Uses Qt worker threads (`QRunnable` + signals) to keep UI responsive.

### 3) Optional API layer: `personal_ai/api/`

- FastAPI app to expose backend functionality without changing CLI behavior.
- Endpoints:
  - `POST /ask`
  - `GET /status`
  - `GET /reminders`
- API is optional and intended for future web/mobile integrations.

### 4) Future web UI placeholder: `ui-web/`

- Contains documentation only for now.
- Intended for a React frontend that consumes the FastAPI API.

## Runtime modes

- Mode detection remains in `personal_ai/core/config.py`.
- The assistant can run in `local` or `dev` mode, depending on environment/dependency availability.

## Testing

- Existing pytest suite in `tests/` remains supported.
- Packaging keeps pytest config in `pyproject.toml`.
