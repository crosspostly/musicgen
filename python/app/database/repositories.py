"""
Repository classes for CRUD operations on Job, Track, and Loop entities.

Provides:
- JobRepository: CRUD operations and queries for Job records
- TrackRepository: CRUD operations and queries for Track records
- LoopRepository: CRUD operations and queries for Loop records
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Job, Track, Loop


class JobRepository:
    """Repository for Job entity operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        job_id: str,
        job_type: str,
        status: str = "pending",
        prompt: Optional[str] = None,
        job_metadata: Optional[Dict[str, Any]] = None,
    ) -> Job:
        """Create a new job record."""
        job = Job(
            job_id=job_id,
            job_type=job_type,
            status=status,
            prompt=prompt,
            job_metadata=job_metadata or {},
        )
        self.session.add(job)
        self.session.commit()
        return job
    
    def get_by_id(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""
        return self.session.query(Job).filter(Job.job_id == job_id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Job]:
        """Retrieve all jobs with pagination."""
        return self.session.query(Job).limit(limit).offset(offset).all()
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Job]:
        """Retrieve jobs by status."""
        return self.session.query(Job).filter(Job.status == status).limit(limit).all()
    
    def update(
        self,
        job_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        error: Optional[str] = None,
        job_metadata: Optional[Dict[str, Any]] = None,
        file_manifest: Optional[Dict[str, Any]] = None,
    ) -> Optional[Job]:
        """Update an existing job record."""
        job = self.get_by_id(job_id)
        if not job:
            return None
        
        if status is not None:
            job.status = status
        if progress is not None:
            job.progress = progress
        if error is not None:
            job.error = error
        if job_metadata is not None:
            job.job_metadata = job_metadata
        if file_manifest is not None:
            job.file_manifest = file_manifest
        
        job.updated_at = datetime.utcnow()
        self.session.commit()
        return job
    
    def delete(self, job_id: str) -> bool:
        """Delete a job record and associated tracks/loops."""
        job = self.get_by_id(job_id)
        if not job:
            return False
        
        self.session.delete(job)
        self.session.commit()
        return True


class TrackRepository:
    """Repository for Track entity operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        track_id: str,
        job_id: str,
        duration: Optional[float] = None,
        track_metadata: Optional[Dict[str, Any]] = None,
        file_path_wav: Optional[str] = None,
        file_path_mp3: Optional[str] = None,
    ) -> Track:
        """Create a new track record."""
        track = Track(
            track_id=track_id,
            job_id=job_id,
            duration=duration,
            track_metadata=track_metadata or {},
            file_path_wav=file_path_wav,
            file_path_mp3=file_path_mp3,
        )
        self.session.add(track)
        self.session.commit()
        return track
    
    def get_by_id(self, track_id: str) -> Optional[Track]:
        """Retrieve a track by ID."""
        return self.session.query(Track).filter(Track.track_id == track_id).first()
    
    def get_by_job_id(self, job_id: str) -> List[Track]:
        """Retrieve all tracks for a given job."""
        return self.session.query(Track).filter(Track.job_id == job_id).all()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Track]:
        """Retrieve all tracks with pagination."""
        return self.session.query(Track).limit(limit).offset(offset).all()
    
    def update(
        self,
        track_id: str,
        duration: Optional[float] = None,
        track_metadata: Optional[Dict[str, Any]] = None,
        file_path_wav: Optional[str] = None,
        file_path_mp3: Optional[str] = None,
    ) -> Optional[Track]:
        """Update an existing track record."""
        track = self.get_by_id(track_id)
        if not track:
            return None
        
        if duration is not None:
            track.duration = duration
        if track_metadata is not None:
            track.track_metadata = track_metadata
        if file_path_wav is not None:
            track.file_path_wav = file_path_wav
        if file_path_mp3 is not None:
            track.file_path_mp3 = file_path_mp3
        
        track.updated_at = datetime.utcnow()
        self.session.commit()
        return track
    
    def delete(self, track_id: str) -> bool:
        """Delete a track record and associated loops."""
        track = self.get_by_id(track_id)
        if not track:
            return False
        
        self.session.delete(track)
        self.session.commit()
        return True


class LoopRepository:
    """Repository for Loop entity operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        loop_id: str,
        track_id: str,
        duration: int,
        fade_in_out: int = 0,
        format: str = "MP3",
        status: str = "PENDING",
    ) -> Loop:
        """Create a new loop record."""
        loop = Loop(
            loop_id=loop_id,
            track_id=track_id,
            duration=duration,
            fade_in_out=fade_in_out,
            format=format,
            status=status,
        )
        self.session.add(loop)
        self.session.commit()
        return loop
    
    def get_by_id(self, loop_id: str) -> Optional[Loop]:
        """Retrieve a loop by ID."""
        return self.session.query(Loop).filter(Loop.loop_id == loop_id).first()
    
    def get_by_track_id(self, track_id: str) -> List[Loop]:
        """Retrieve all loops for a given track."""
        return self.session.query(Loop).filter(Loop.track_id == track_id).all()
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Loop]:
        """Retrieve loops by status."""
        return self.session.query(Loop).filter(Loop.status == status).limit(limit).all()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Loop]:
        """Retrieve all loops with pagination."""
        return self.session.query(Loop).limit(limit).offset(offset).all()
    
    def update(
        self,
        loop_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        error: Optional[str] = None,
        result_url: Optional[str] = None,
        result_path: Optional[str] = None,
    ) -> Optional[Loop]:
        """Update an existing loop record."""
        loop = self.get_by_id(loop_id)
        if not loop:
            return None
        
        if status is not None:
            loop.status = status
        if progress is not None:
            loop.progress = progress
        if error is not None:
            loop.error = error
        if result_url is not None:
            loop.result_url = result_url
        if result_path is not None:
            loop.result_path = result_path
        
        loop.updated_at = datetime.utcnow()
        self.session.commit()
        return loop
    
    def delete(self, loop_id: str) -> bool:
        """Delete a loop record."""
        loop = self.get_by_id(loop_id)
        if not loop:
            return False
        
        self.session.delete(loop)
        self.session.commit()
        return True
