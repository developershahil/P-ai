# Getting Started

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev]
```

## Run CLI assistant
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

## Run tests
```bash
pytest -q
```
