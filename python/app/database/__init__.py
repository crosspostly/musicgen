"""
Database module for DiffRhythm service.

Provides SQLAlchemy models, session management, and repositories
for Job, Track, and Loop entities with SQLite persistence.

Exports:
- Base: SQLAlchemy declarative base
- Models: Job, Track, Loop
- Repositories: JobRepository, TrackRepository, LoopRepository
- Session utilities: get_session, init_database
"""

from app.database.base import Base
from app.database.models import Job, Track, Loop
from app.database.repositories import (
    JobRepository,
    TrackRepository,
    LoopRepository,
)
from app.database.session import (
    get_session,
    init_database,
    create_db_engine,
    SessionLocal,
)

__all__ = [
    "Base",
    "Job",
    "Track",
    "Loop",
    "JobRepository",
    "TrackRepository",
    "LoopRepository",
    "get_session",
    "init_database",
    "create_db_engine",
    "SessionLocal",
]
