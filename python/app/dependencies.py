from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from .config import Settings, get_settings
from .db import get_db_session


def get_settings_dependency() -> Settings:
    """FastAPI dependency that returns application settings."""
    return get_settings()


def get_db_session_dependency() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    yield from get_db_session()
