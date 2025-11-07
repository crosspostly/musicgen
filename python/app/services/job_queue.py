"""
Job Queue Service

Provides queued/processing/completed/failed states, progress tracking,
and optional Redis integration, persisted in SQLite.
"""

import os
import uuid
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..core.database import get_db
from ..models.job import Job, JobStatus

logger = logging.getLogger(__name__)


class JobQueueService:
    """
    Job queue service with SQLite persistence and Redis hooks
    """
    
    def __init__(self, db: Optional[Session] = None, redis_enabled: bool = False):
        """
        Initialize job queue service
        
        Args:
            db: Database session (if None, will use dependency injection)
            redis_enabled: Whether to enable Redis integration (future feature)
        """
        self._db = db
        self.redis_enabled = redis_enabled and os.getenv("REDIS_URL")
        
        # Initialize Redis client if enabled (future implementation)
        if self.redis_enabled:
            try:
                import redis
                self.redis_client = redis.from_url(os.getenv("REDIS_URL"))
                logger.info("Redis integration enabled for job queue")
            except ImportError:
                logger.warning("Redis not available, falling back to SQLite only")
                self.redis_enabled = False
                self.redis_client = None
        else:
            self.redis_client = None
    
    @contextmanager
    def get_db_session(self):
        """Get database session context manager"""
        if self._db:
            yield self._db
        else:
            db_gen = get_db()
            db = next(db_gen)
            try:
                yield db
            finally:
                db.close()
    
    def enqueue_job(
        self,
        job_type: str,
        request_data: Dict[str, Any],
        priority: int = 0,
        status: JobStatus = JobStatus.QUEUED
    ) -> str:
        """
        Enqueue a new job
        
        Args:
            job_type: Type of job (e.g., "diffrhythm", "loop", "export")
            request_data: Job request parameters
            priority: Job priority (higher = more important)
            status: Initial job status
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        with self.get_db_session() as db:
            job = Job(
                id=job_id,
                job_type=job_type,
                status=status,
                priority=priority,
                request_data=request_data
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            # Redis integration hook (future)
            if self.redis_enabled:
                self._redis_enqueue_job(job_id, job_type, priority)
            
            logger.info(f"Enqueued job {job_id} of type {job_type}")
            return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job object or None if not found
        """
        with self.get_db_session() as db:
            return db.query(Job).filter(Job.id == job_id).first()
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
        worker_id: Optional[str] = None
    ) -> bool:
        """
        Update job status and/or progress
        
        Args:
            job_id: Job identifier
            status: New job status
            progress: Progress percentage (0-100)
            message: Status message
            error: Error message
            result_data: Result metadata
            worker_id: Worker ID processing the job
            
        Returns:
            True if updated, False if job not found
        """
        with self.get_db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False
            
            # Update fields
            if status is not None:
                job.status = status
                
                # Auto-set timestamps for status changes
                if status == JobStatus.PROCESSING and not job.started_at:
                    job.mark_started(worker_id)
                elif status == JobStatus.COMPLETED:
                    job.mark_completed(result_data)
                elif status == JobStatus.FAILED:
                    job.mark_failed(error or "Unknown error", message)
            
            if progress is not None:
                job.progress = max(0, min(100, progress))
            
            if message is not None:
                job.message = message
            
            if error is not None:
                job.error = error
            
            if result_data is not None:
                job.result_data = result_data
            
            if worker_id is not None:
                job.worker_id = worker_id
            
            db.commit()
            
            # Redis integration hook (future)
            if self.redis_enabled:
                self._redis_update_job(job_id, status, progress)
            
            return True
    
    def update_progress(self, job_id: str, progress: int, message: Optional[str] = None) -> bool:
        """
        Convenience method to update job progress
        
        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
            message: Optional progress message
            
        Returns:
            True if updated, False if job not found
        """
        return self.update_job(job_id, progress=progress, message=message)
    
    def list_jobs(
        self,
        status: Optional[Union[JobStatus, List[JobStatus]]] = None,
        job_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at"
    ) -> List[Job]:
        """
        List jobs with optional filtering
        
        Args:
            status: Filter by status (single or list)
            job_type: Filter by job type
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            order_by: Field to order by (created_at, updated_at, priority)
            
        Returns:
            List of jobs
        """
        with self.get_db_session() as db:
            query = db.query(Job)
            
            # Apply filters
            if status:
                if isinstance(status, list):
                    query = query.filter(Job.status.in_(status))
                else:
                    query = query.filter(Job.status == status)
            
            if job_type:
                query = query.filter(Job.job_type == job_type)
            
            # Apply ordering
            if order_by == "priority":
                query = query.order_by(desc(Job.priority), Job.created_at)
            elif order_by == "updated_at":
                query = query.order_by(desc(Job.updated_at))
            else:  # created_at (default)
                query = query.order_by(desc(Job.created_at))
            
            # Apply pagination
            return query.offset(offset).limit(limit).all()
    
    def get_next_job(
        self,
        job_types: Optional[List[str]] = None,
        worker_id: Optional[str] = None
    ) -> Optional[Job]:
        """
        Get next available job for processing
        
        Args:
            job_types: List of job types this worker can handle
            worker_id: Worker ID requesting the job
            
        Returns:
            Next available job or None
        """
        with self.get_db_session() as db:
            # Build query for available jobs
            query = db.query(Job).filter(
                Job.status.in_([JobStatus.QUEUED, JobStatus.PENDING])
            )
            
            if job_types:
                query = query.filter(Job.job_type.in_(job_types))
            
            # Order by priority (high to low) then creation time
            job = query.order_by(desc(Job.priority), Job.created_at).first()
            
            if job and worker_id:
                # Mark as being processed by this worker
                job.status = JobStatus.PROCESSING
                job.mark_started(worker_id)
                db.commit()
                
                # Redis integration hook (future)
                if self.redis_enabled:
                    self._redis_claim_job(job.id, worker_id)
            
            return job
    
    def get_job_stats(self, job_type: Optional[str] = None) -> Dict[str, int]:
        """
        Get job statistics
        
        Args:
            job_type: Filter by job type
            
        Returns:
            Dictionary with job counts by status
        """
        with self.get_db_session() as db:
            query = db.query(Job)
            
            if job_type:
                query = query.filter(Job.job_type == job_type)
            
            # Count by status
            stats = {}
            for status in JobStatus:
                count = query.filter(Job.status == status).count()
                stats[status.value] = count
            
            # Add totals
            stats["total"] = query.count()
            stats["active"] = sum(
                count for status, count in stats.items()
                if status in [s.value for s in JobStatus if s != JobStatus.COMPLETED and s != JobStatus.FAILED]
            )
            
            return stats
    
    def cleanup_old_jobs(self, days: int = 30, status: Optional[JobStatus] = None) -> int:
        """
        Clean up old jobs
        
        Args:
            days: Age threshold in days
            status: Only clean up jobs with this status (None for all)
            
        Returns:
            Number of jobs cleaned up
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        with self.get_db_session() as db:
            query = db.query(Job).filter(Job.created_at < cutoff_date)
            
            if status:
                query = query.filter(Job.status == status)
            
            # Only clean up finished jobs by default
            if status is None:
                query = query.filter(
                    or_(Job.status == JobStatus.COMPLETED, Job.status == JobStatus.FAILED)
                )
            
            count = query.count()
            query.delete()
            db.commit()
            
            logger.info(f"Cleaned up {count} old jobs")
            return count
    
    # Redis integration methods (future implementation)
    def _redis_enqueue_job(self, job_id: str, job_type: str, priority: int):
        """Hook for Redis job enqueue (future)"""
        if self.redis_client:
            # Future: Add job to Redis queue
            pass
    
    def _redis_update_job(self, job_id: str, status: Optional[JobStatus], progress: Optional[int]):
        """Hook for Redis job update (future)"""
        if self.redis_client:
            # Future: Update job status in Redis
            pass
    
    def _redis_claim_job(self, job_id: str, worker_id: str):
        """Hook for Redis job claiming (future)"""
        if self.redis_client:
            # Future: Claim job in Redis
            pass