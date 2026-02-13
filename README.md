# Personal AI

A modular Python personal assistant platform with:

- **Backend package** (`personal_ai/`) for assistant logic.
- **Desktop UI** (`ui-desktop/`) powered by PySide6.
- **Optional FastAPI layer** (`personal_ai/api/`) for future integrations.
- **Future web UI placeholder** (`ui-web/`) for planned React frontend work.

## Repository structure

```text
.
├── personal_ai/              # Backend package + CLI + optional API
├── ui-desktop/               # PySide6 desktop application
├── ui-web/                   # Placeholder for future web UI (docs only)
├── docs/                     # Architecture and setup docs
├── tests/                    # Pytest suite
├── pyproject.toml            # Packaging and tool config
├── requirements.txt          # Runtime dependencies
└── README.md
```

For architecture details, see `docs/ARCHITECTURE.md`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev]
```

## Run the CLI assistant (unchanged)

```bash
python -m personal_ai.main
```

or via script entrypoint:

```bash
personal-ai
```

## Run the desktop UI (PySide6)

```bash
python ui-desktop/main_window.py
```

## Run the optional API server (FastAPI)

Install API extras (optional):

```bash
pip install -e .[api]
```

Then run:

```bash
uvicorn personal_ai.api.app:app --reload
```

### API endpoints

- `POST /ask`
- `GET /status`
- `GET /reminders`

## Run tests

```bash
pytest -q
```
