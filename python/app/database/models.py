"""
SQLAlchemy models for Job, Track, and Loop persistence.

Models:
- Job: Represents a generation job with status, prompts, and file manifest
- Track: Represents a generated track linked to a job
- Loop: Represents a loop variant created from a track
"""

from datetime import datetime
from typing import Optional, Any
import uuid

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base


class Job(Base):
    """
    Job model for tracking music generation jobs.
    
    Fields:
    - job_id: Unique job identifier (UUID)
    - job_type: Type of job (e.g., 'diffrhythm', 'yue', 'bark', 'lyria', 'magnet')
    - status: Current job status (pending, loading_model, preparing_prompt, generating_audio, exporting, completed, failed)
    - progress: Progress percentage (0-100)
    - prompt: Original text prompt used for generation
    - metadata: JSON metadata (language, genre, mood, etc.)
    - file_manifest: JSON containing file paths and URLs (wav_path, mp3_path, etc.)
    - error: Error message if job failed
    - created_at: Job creation timestamp
    - updated_at: Last update timestamp
    
    Relationships:
    - tracks: One-to-many relationship with Track
    """
    
    __tablename__ = "jobs"
    
    job_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(50), nullable=False, default="diffrhythm")
    status = Column(String(50), nullable=False, default="pending")
    progress = Column(Integer, nullable=False, default=0)
    prompt = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True, default=dict)
    file_manifest = Column(JSON, nullable=True, default=dict)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tracks = relationship("Track", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Job(job_id={self.job_id}, status={self.status}, progress={self.progress})>"


class Track(Base):
    """
    Track model representing a generated music track.
    
    Fields:
    - track_id: Unique track identifier (UUID)
    - job_id: Foreign key to Job
    - duration: Duration of the track in seconds
    - metadata: JSON metadata (artist, album, genre, track_name, etc.)
    - file_path_wav: Path to WAV file
    - file_path_mp3: Path to MP3 file
    - created_at: Track creation timestamp
    - updated_at: Last update timestamp
    
    Relationships:
    - job: Many-to-one relationship with Job
    - loops: One-to-many relationship with Loop
    """
    
    __tablename__ = "tracks"
    
    track_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.job_id"), nullable=False)
    duration = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True, default=dict)
    file_path_wav = Column(Text, nullable=True)
    file_path_mp3 = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="tracks")
    loops = relationship("Loop", back_populates="track", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Track(track_id={self.track_id}, job_id={self.job_id}, duration={self.duration})>"


class Loop(Base):
    """
    Loop model representing a looped variant of a track.
    
    Fields:
    - loop_id: Unique loop identifier (UUID)
    - track_id: Foreign key to Track
    - status: Current status (PENDING, ANALYZING, RENDERING, EXPORTING, COMPLETED, FAILED)
    - duration: Loop duration in seconds
    - fade_in_out: Boolean indicating if fade in/out is applied
    - format: Audio format (MP3, WAV)
    - progress: Progress percentage (0-100)
    - error: Error message if loop creation failed
    - result_url: URL for downloading the loop
    - result_path: File system path to the result
    - created_at: Loop creation timestamp
    - updated_at: Last update timestamp
    
    Relationships:
    - track: Many-to-one relationship with Track
    """
    
    __tablename__ = "loops"
    
    loop_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    track_id = Column(String(36), ForeignKey("tracks.track_id"), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    duration = Column(Integer, nullable=False)
    fade_in_out = Column(Integer, nullable=False, default=0)  # 0 or 1
    format = Column(String(10), nullable=False, default="MP3")
    progress = Column(Integer, nullable=False, default=0)
    error = Column(Text, nullable=True)
    result_url = Column(Text, nullable=True)
    result_path = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    track = relationship("Track", back_populates="loops")
    
    def __repr__(self) -> str:
        return f"<Loop(loop_id={self.loop_id}, track_id={self.track_id}, status={self.status})>"
