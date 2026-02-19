# Development Workflow

## 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev,api]
cp .env.example .env
```

## 2) Test locally

```bash
pytest -q
```

## 3) Retrain model

```bash
python scripts/retrain_model.py
```

## 4) Run API with auth

Set `API_KEY` in `.env`, then:

```bash
uvicorn personal_ai.api.app:app --reload
```

Use `x-api-key` header in requests.

## 5) CI

GitHub Actions workflow `.github/workflows/ci.yml` runs tests on push and pull request.
