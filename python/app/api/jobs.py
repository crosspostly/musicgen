"""
Job API endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field

from ..dependencies import get_job_queue_service, get_job_by_id
from ..models.job import Job, JobStatus
from ..services.job_queue import JobQueueService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# Pydantic models for API
class JobResponse(BaseModel):
    """Job response model"""
    id: str
    status: str
    progress: int
    job_type: str
    priority: int
    request_data: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response model"""
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int


class JobStatsResponse(BaseModel):
    """Job statistics response model"""
    queued: int = 0
    pending: int = 0
    processing: int = 0
    loading_model: int = 0
    preparing_prompt: int = 0
    generating_audio: int = 0
    exporting: int = 0
    analyzing: int = 0
    rendering: int = 0
    completed: int = 0
    failed: int = 0
    total: int = 0
    active: int = 0


class JobCreateRequest(BaseModel):
    """Job creation request model"""
    job_type: str = Field(..., description="Type of job to create")
    request_data: Dict[str, Any] = Field(..., description="Job parameters")
    priority: int = Field(default=0, ge=0, le=100, description="Job priority (0-100)")
    status: str = Field(default=JobStatus.QUEUED, description="Initial job status")


class JobUpdateRequest(BaseModel):
    """Job update request model"""
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    message: Optional[str] = None
    error: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job: Job = Depends(get_job_by_id)
):
    """
    Get job status and details
    
    Args:
        job: Job from dependency
        
    Returns:
        Job details
    """
    return JobResponse.from_orm(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_update: JobUpdateRequest,
    job: Job = Depends(get_job_by_id),
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Update job status, progress, or metadata
    
    Args:
        job_update: Update data
        job: Job from dependency
        queue_service: Job queue service
        
    Returns:
        Updated job details
    """
    # Validate status if provided
    status_enum = None
    if job_update.status:
        try:
            status_enum = JobStatus(job_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {job_update.status}"
            )
    
    # Update job
    updated = queue_service.update_job(
        job.id,
        status=status_enum,
        progress=job_update.progress,
        message=job_update.message,
        error=job_update.error,
        result_data=job_update.result_data
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job"
        )
    
    # Get updated job
    updated_job = queue_service.get_job(job.id)
    return JobResponse.from_orm(updated_job)


@router.post("", response_model=JobResponse)
async def create_job(
    job_request: JobCreateRequest,
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Create a new job
    
    Args:
        job_request: Job creation data
        queue_service: Job queue service
        
    Returns:
        Created job details
    """
    # Validate status
    try:
        status_enum = JobStatus(job_request.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {job_request.status}"
        )
    
    # Create job
    job_id = queue_service.enqueue_job(
        job_type=job_request.job_type,
        request_data=job_request.request_data,
        priority=job_request.priority,
        status=status_enum
    )
    
    # Get created job
    job = queue_service.get_job(job_id)
    return JobResponse.from_orm(job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    order_by: str = Query("created_at", pattern="^(created_at|updated_at|priority)$", description="Order by field"),
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    List jobs with optional filtering
    
    Args:
        status: Filter by status
        job_type: Filter by job type
        limit: Maximum number of jobs
        offset: Number of jobs to skip
        order_by: Field to order by
        queue_service: Job queue service
        
    Returns:
        List of jobs
    """
    # Parse status filter
    status_filter = None
    if status:
        try:
            status_filter = JobStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Get jobs
    jobs = queue_service.list_jobs(
        status=status_filter,
        job_type=job_type,
        limit=limit,
        offset=offset,
        order_by=order_by
    )
    
    # Get total count (simplified - in production would use separate count query)
    total = len(queue_service.list_jobs(
        status=status_filter,
        job_type=job_type,
        limit=10000,  # Large limit for counting
        offset=0
    ))
    
    return JobListResponse(
        jobs=[JobResponse.from_orm(job) for job in jobs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/stats/{job_type}", response_model=JobStatsResponse)
async def get_job_stats_by_type(
    job_type: str,
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Get job statistics for specific type
    
    Args:
        job_type: Job type to get stats for
        queue_service: Job queue service
        
    Returns:
        Job statistics
    """
    stats = queue_service.get_job_stats(job_type=job_type)
    return JobStatsResponse(**stats)


@router.get("/stats", response_model=JobStatsResponse)
async def get_job_stats(
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Get overall job statistics
    
    Args:
        queue_service: Job queue service
        
    Returns:
        Job statistics
    """
    stats = queue_service.get_job_stats()
    return JobStatsResponse(**stats)


@router.post("/{job_id}/progress", response_model=JobResponse)
async def update_job_progress(
    progress: int = Query(..., ge=0, le=100, description="Progress percentage (0-100)"),
    message: Optional[str] = Query(None, description="Progress message"),
    job: Job = Depends(get_job_by_id),
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Update job progress
    
    Args:
        progress: Progress percentage
        message: Optional progress message
        job: Job from dependency
        queue_service: Job queue service
        
    Returns:
        Updated job details
    """
    updated = queue_service.update_progress(job.id, progress, message)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job progress"
        )
    
    # Get updated job
    updated_job = queue_service.get_job(job.id)
    return JobResponse.from_orm(updated_job)


@router.delete("/{job_id}")
async def delete_job(
    job: Job = Depends(get_job_by_id),
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Delete a job (only completed or failed jobs)
    
    Args:
        job: Job from dependency
        queue_service: Job queue service
        
    Returns:
        Success message
    """
    if job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active job"
        )
    
    # Delete job from database
    with queue_service.get_db_session() as db:
        db.delete(job)
        db.commit()
    
    return {"message": f"Job {job.id} deleted successfully"}