"""
FastAPI dependencies for job queue service and DiffRhythm service
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .core.database import get_db
from .services.job_queue import JobQueueService
from .services.diffrhythm import DiffRhythmService
from .models.job import Job, JobStatus


def get_job_queue_service(db: Session = Depends(get_db)) -> JobQueueService:
    """
    Dependency to get job queue service instance
    
    Args:
        db: Database session
        
    Returns:
        JobQueueService instance
    """
    redis_enabled = False  # Can be made configurable via environment
    return JobQueueService(db=db, redis_enabled=redis_enabled)


def get_job_by_id(
    job_id: str,
    queue_service: JobQueueService = Depends(get_job_queue_service)
) -> Job:
    """
    Dependency to get job by ID, raises 404 if not found
    
    Args:
        job_id: Job identifier
        queue_service: Job queue service
        
    Returns:
        Job object
        
    Raises:
        HTTPException: If job not found
    """
    job = queue_service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    return job


def get_active_job_by_id(
    job_id: str,
    queue_service: JobQueueService = Depends(get_job_queue_service)
) -> Job:
    """
    Dependency to get active job by ID, raises 404 if not found or not active
    
    Args:
        job_id: Job identifier
        queue_service: Job queue service
        
    Returns:
        Active Job object
        
    Raises:
        HTTPException: If job not found or not active
    """
    job = get_job_by_id(job_id, queue_service)
    
    if not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not active (status: {job.status})"
        )
    
    return job


def get_completed_job_by_id(
    job_id: str,
    queue_service: JobQueueService = Depends(get_job_queue_service)
) -> Job:
    """
    Dependency to get completed job by ID, raises 404 if not found or not completed
    
    Args:
        job_id: Job identifier
        queue_service: Job queue service
        
    Returns:
        Completed Job object
        
    Raises:
        HTTPException: If job not found or not completed
    """
    job = get_job_by_id(job_id, queue_service)
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not completed (status: {job.status})"
        )
    
    return job


# Module-level service instance (will be set on app startup)
_diffrhythm_service: Optional[DiffRhythmService] = None


def set_diffrhythm_service(service: DiffRhythmService) -> None:
    """Set the DiffRhythm service instance (called on app startup)"""
    global _diffrhythm_service
    _diffrhythm_service = service


def get_diffrhythm_service() -> DiffRhythmService:
    """
    Dependency to get DiffRhythm service instance.
    
    The service is initialized on application startup and stored globally.
    
    Returns:
        DiffRhythmService instance
        
    Raises:
        RuntimeError: If service is not available (not initialized on startup)
    """
    if _diffrhythm_service is None:
        raise RuntimeError("DiffRhythm service not initialized on startup")
    return _diffrhythm_service