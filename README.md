# Personal AI

A modular Python personal assistant project organized with a modern `src/` layout.

## Project layout

```text
personal_ai/
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── docs/
│   └── getting_started.md
├── pyproject.toml
├── requirements.txt
├── scripts/
│   └── safe_version.py
├── src/
│   └── personal_ai/
│       ├── __init__.py
│       ├── actions/
│       ├── core/
│       ├── data/
│       ├── entities/
│       ├── learning/
│       ├── ml/
│       ├── reminders/
│       ├── security/
│       ├── ui/
│       ├── voice/
│       └── main.py
└── tests/
    ├── __init__.py
    ├── test_entities.py
    ├── test_parser.py
    └── test_reminders.py
```

> Note: Compatibility wrappers are preserved for legacy imports (`core/entities.py`, `core/parser.py`) while new package entrypoints live under `personal_ai.entities` and `personal_ai.parser`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Run the app:

```bash
python -m personal_ai.main
```

Run tests:

```bash
pytest -q
```
