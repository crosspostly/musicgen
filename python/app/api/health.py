from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..config import Settings
from ..dependencies import get_settings_dependency
from ..db import check_database_connection

router = APIRouter()


@router.get("/health")
def health_check(settings: Settings = Depends(get_settings_dependency)) -> dict[str, object]:
    """Return application health information."""
    database_ok, database_error = check_database_connection()

    storage_path = settings.storage_dir
    storage_exists = storage_path.exists()
    storage_writable = os.access(storage_path, os.W_OK) if storage_exists else False

    cache_path = settings.model_cache_dir
    cache_exists = cache_path.exists()
    cache_writable = os.access(cache_path, os.W_OK) if cache_exists else False

    healthy = database_ok and storage_exists and cache_exists

    return {
        "status": "ok" if healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
        "version": settings.api_version,
        "database": {
            "connected": database_ok,
            "url": settings.database_url,
            "error": database_error,
        },
        "storage": {
            "path": str(storage_path),
            "exists": storage_exists,
            "writable": storage_writable,
        },
        "modelCache": {
            "path": str(cache_path),
            "exists": cache_exists,
            "writable": cache_writable,
            "status": "ready" if cache_exists else "missing",
        },
        "redis": {
            "configured": settings.redis_url is not None,
            "url": settings.redis_url,
        },
    }
