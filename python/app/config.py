from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = PROJECT_ROOT / "python"
DEFAULT_STORAGE_DIR = PROJECT_ROOT / "storage"
DEFAULT_MODEL_CACHE_DIR = PROJECT_ROOT / "models" / "cache"
DEFAULT_SQLITE_PATH = DEFAULT_STORAGE_DIR / "app.db"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(
            str(PYTHON_DIR / ".env"),
            str(PROJECT_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = Field(default="DiffRhythm FastAPI Service", alias="APP_NAME")
    api_version: str = Field(default="0.1.0", alias="API_VERSION")
    environment: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(default=f"sqlite:///{DEFAULT_SQLITE_PATH}", alias="DATABASE_URL")
    storage_dir: Path = Field(default=DEFAULT_STORAGE_DIR, alias="STORAGE_DIR")
    model_cache_dir: Path = Field(default=DEFAULT_MODEL_CACHE_DIR, alias="MODEL_CACHE_DIR")
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")

    docs_url: Optional[str] = Field(default="/docs", alias="DOCS_URL")
    redoc_url: Optional[str] = Field(default="/redoc", alias="REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", alias="OPENAPI_URL")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_HEADERS")

    def ensure_directories(self) -> None:
        """Ensure storage and cache directories exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)

        sqlite_path = self.sqlite_file_path
        if sqlite_path is not None:
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def sqlite_file_path(self) -> Optional[Path]:
        if not self.database_url.startswith("sqlite"):
            return None

        url = make_url(self.database_url)
        if url.database in (None, ":memory:"):
            return None

        return Path(url.database).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
