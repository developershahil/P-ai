# Implementation Reference

## Purpose

This document is a practical reference for what is implemented now, what changed in this update, and the logic used.

## Implemented and Working

- Centralized config with `.env` loading in `personal_ai/core/config.py`.
- Structured file logging (info/error) in `personal_ai/core/logging_config.py`.
- API key middleware for FastAPI in `personal_ai/api/app.py`.
- Model evaluation metrics (accuracy, macro F1, confusion matrix) and model versioning in `personal_ai/learning/trainer.py`.
- Retraining entry script `scripts/retrain_model.py`.
- Packaging/build script `scripts/build_executable.py`.
- Preference persistence (`profile.json`) in `personal_ai/core/profile.py` (currently stores `last_intent`).
- CI workflow `.github/workflows/ci.yml`.

## What Needed Change (and is now covered)

1. ML evaluation and version tracking.
2. Simple retraining pipeline.
3. Better unit test coverage for assistant + reminder time parsing (parser/entities/reminders already present and expanded).
4. Continuous test execution on push/PR.
5. API auth for production-like usage.
6. Standalone packaging path.
7. Unified settings source with env overrides.
8. Persistent logs for diagnostics.
9. Lightweight user preference persistence.
10. Documentation for auth/dev workflow/roadmap.

## Logic Notes

- **Model promotion logic**: candidate is promoted only when accuracy or macro-F1 improves beyond threshold (`MODEL_IMPROVEMENT_THRESHOLD`).
- **Versioning logic**: model version increments only on promotion; otherwise version remains unchanged.
- **API auth logic**: auth is optional; if `API_KEY` is empty, middleware allows all requests.
- **Logging logic**: JSON-line logs are written to separate app and error files with rotating handlers.
- **Profile logic**: profile is read/written from `personal_ai/data/profile.json`, with safe defaults on missing/corrupt files.

## Current Validation State

- Unit tests verify parser, entity extraction, reminder scheduling + reminder time parsing, and core `handle_input` behavior.
- CI runs `pytest -q` automatically for push and pull_request.
