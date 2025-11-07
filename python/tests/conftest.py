from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

# Configure an isolated environment for tests before importing the app.
TEST_ROOT = Path(tempfile.mkdtemp(prefix="fastapi-tests-"))
STORAGE_DIR = TEST_ROOT / "storage"
MODEL_CACHE_DIR = TEST_ROOT / "model-cache"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = STORAGE_DIR / "test.sqlite"

os.environ.setdefault("DATABASE_URL", f"sqlite:///{DB_PATH}")
os.environ.setdefault("STORAGE_DIR", str(STORAGE_DIR))
os.environ.setdefault("MODEL_CACHE_DIR", str(MODEL_CACHE_DIR))
os.environ.setdefault("LOG_LEVEL", "WARNING")

from app.config import Settings, get_settings  # noqa: E402

get_settings.cache_clear()


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    from app.main import create_app

    application = create_app()
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session", autouse=True)
def cleanup_environment() -> Iterator[None]:
    try:
        yield
    finally:
        shutil.rmtree(TEST_ROOT, ignore_errors=True)
