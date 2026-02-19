# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-19
### Release
- First stable release of Personal AI Assistant across CLI, desktop (PySide6), and FastAPI surfaces.

### Highlights
- Core assistant capabilities finalized: intent handling with ML + fallback rules, reminders, notes, entity extraction, command splitting, and safety permissions.
- Production-readiness improvements completed: expanded test suite, GitHub Actions CI on push/PR, structured file logging, API key middleware, and executable packaging workflow.
- ML operations improvements included: retraining script, model metrics output (accuracy/F1/confusion matrix), and model version tracking.

## [0.1.0] - 2026-02-13
### Added
- Refactored repository to a `src/` layout with cleaner package organization.
- Introduced top-level `tests/`, `docs/`, and `scripts/` folders.
- Added packaging metadata updates in `pyproject.toml` and editable install workflow.
- Added contribution/community templates and UI stub module.
