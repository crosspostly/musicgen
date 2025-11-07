"""
Job model for persistent job queue storage
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from enum import Enum

from ..core.database import Base


class JobStatus(str, Enum):
    """Job status enum matching backend requirements"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
    # Extended statuses for specific generators
    PENDING = "pending"
    LOADING_MODEL = "loading_model"
    PREPARING_PROMPT = "preparing_prompt"
    GENERATING_AUDIO = "generating_audio"
    EXPORTING = "exporting"
    ANALYZING = "analyzing"
    RENDERING = "rendering"


class Job(Base):
    """
    Job model for persistent storage
    """
    __tablename__ = "jobs"
    
    # Primary fields
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default=JobStatus.QUEUED, nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False)
    
    # Job metadata
    job_type = Column(String, nullable=False, index=True)  # e.g., "diffrhythm", "loop", "export"
    priority = Column(Integer, default=0, nullable=False, index=True)  # Higher number = higher priority
    
    # Request data
    request_data = Column(JSON, nullable=True)  # Original request parameters
    
    # Result data
    result_data = Column(JSON, nullable=True)  # Result metadata, file paths, etc.
    
    # Status tracking
    message = Column(Text, nullable=True)  # Human-readable status message
    error = Column(Text, nullable=True)   # Error details if failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Worker tracking
    worker_id = Column(String, nullable=True, index=True)  # Which worker is processing this job
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary representation"""
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "job_type": self.job_type,
            "priority": self.priority,
            "request_data": self.request_data,
            "result_data": self.result_data,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "worker_id": self.worker_id
        }
    
    @property
    def is_finished(self) -> bool:
        """Check if job is in a terminal state"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED]
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently being processed"""
        return self.status in [
            JobStatus.QUEUED, JobStatus.PROCESSING, JobStatus.PENDING,
            JobStatus.LOADING_MODEL, JobStatus.PREPARING_PROMPT,
            JobStatus.GENERATING_AUDIO, JobStatus.EXPORTING,
            JobStatus.ANALYZING, JobStatus.RENDERING
        ]
    
    def mark_started(self, worker_id: Optional[str] = None):
        """Mark job as started"""
        self.started_at = datetime.now(timezone.utc)
        self.worker_id = worker_id
    
    def mark_completed(self, result_data: Optional[Dict[str, Any]] = None):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.now(timezone.utc)
        if result_data:
            self.result_data = result_data
        if not self.message:
            self.message = "Job completed successfully"
    
    def mark_failed(self, error: str, message: Optional[str] = None):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error
        if message:
            self.message = message
        elif not self.message:
            self.message = "Job failed"