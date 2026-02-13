# ui-web (placeholder)

This folder is reserved for a future web UI implementation (likely React + TypeScript).

## Planned integration

The web frontend will communicate with the optional FastAPI backend in `personal_ai/api/app.py`:

- `POST /ask` for chat interactions
- `GET /status` for runtime health/mode
- `GET /reminders` for reminder list views

## Suggested future setup

- Build a React app in this folder.
- Add API client utilities for the endpoints above.
- Use environment-based backend URL config for local/dev/prod.

No web UI code is intentionally included yet.
