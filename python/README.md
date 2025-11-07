# DiffRhythm FastAPI Service

This folder contains the Python backend for DiffRhythm. The service is built with FastAPI and is responsible for exposing health and API endpoints, managing configuration, and coordinating persistence through SQLite. The initial skeleton is ready for additional routers and domain logic.

## Quick Start

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # optional, update values as needed
uvicorn app.main:app --reload
```

The server starts on <http://localhost:8000>. Visit `/docs` for the interactive OpenAPI documentation or `/health` for a JSON health report.

## Configuration

Configuration is managed through Pydantic settings and loaded from environment variables (supports `.env`). Key variables include:

- `APP_NAME` – Human-friendly service name (default: `DiffRhythm FastAPI Service`).
- `APP_ENV` – Environment label (`development`, `staging`, `production`).
- `LOG_LEVEL` – Logging verbosity (e.g. `INFO`, `DEBUG`).
- `DATABASE_URL` – SQLAlchemy DSN (default: `sqlite:///../storage/app.db`).
- `STORAGE_DIR` – Directory for generated data and the SQLite file (default: `../storage`).
- `MODEL_CACHE_DIR` – Directory for cached ML models (default: `../models/cache`).
- `REDIS_URL` – Optional Redis connection string.
- `CORS_ALLOW_ORIGINS` – JSON array of allowed origins (default: `[*]`).

The settings loader ensures that storage and model cache directories exist before the application starts.

## Project Structure

```
python/
├── app/
│   ├── __init__.py          # Application package export
│   ├── api/                 # Route modules
│   │   ├── __init__.py
│   │   └── health.py        # Health endpoint
│   ├── config.py            # Pydantic settings and directory helpers
│   ├── db.py                # SQLAlchemy engine/session helpers
│   ├── dependencies.py      # FastAPI dependency utilities
│   └── main.py              # App factory and middleware wiring
├── migrations/              # Alembic scaffolding placeholder
├── tests/
│   ├── conftest.py          # Test client + isolated environment
│   └── test_health.py       # Health endpoint smoke test
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Testing

```bash
cd python
pytest
```

The test suite uses FastAPI's `TestClient` to validate the `/health` endpoint and configuration bootstrapping.

## Database Migrations

Alembic is included in the requirements. Initialise the migration environment when models are introduced:

```bash
cd python
alembic init migrations
```

The generated `env.py` should target models from `app.db.Base`.
