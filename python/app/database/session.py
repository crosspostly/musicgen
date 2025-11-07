"""
Database session management and initialization.

Provides:
- Engine creation and configuration
- Session factory for creating database sessions
- Database initialization on startup
"""

import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.models import Job, Track, Loop

# Database URL configuration
def get_database_url() -> str:
    """Get database URL from environment or use default SQLite."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # Default to SQLite
    db_path = os.getenv("DB_PATH", "./app.db")
    return f"sqlite:///{db_path}"


def create_db_engine() -> Engine:
    """Create SQLAlchemy engine with appropriate configuration."""
    db_url = get_database_url()
    
    if "sqlite" in db_url:
        # SQLite specific configuration
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=os.getenv("SQL_ECHO", "False").lower() == "true"
        )
    else:
        # For other databases (PostgreSQL, MySQL, etc.)
        engine = create_engine(
            db_url,
            echo=os.getenv("SQL_ECHO", "False").lower() == "true"
        )
    
    return engine


def init_db(engine: Engine) -> None:
    """
    Initialize database by creating all tables.
    
    This is called on application startup and creates tables
    if they don't already exist.
    """
    Base.metadata.create_all(bind=engine)


# Global engine and session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """Get a new database session."""
    return SessionLocal()


def init_database() -> None:
    """Initialize database on application startup."""
    init_db(engine)
