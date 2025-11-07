"""
Tests for database models, session management, and repositories.

Tests cover:
- Model creation and field validation
- Persistence and retrieval workflows
- Referential integrity (Track ↔ Job, Loop ↔ Track)
- Repository CRUD operations
- JSON field handling
"""

import sys
import os
import tempfile
import uuid
from datetime import datetime

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import Job, Track, Loop
from app.database.repositories import JobRepository, TrackRepository, LoopRepository
from app.database.session import init_db


@pytest.fixture
def temp_db():
    """Create a temporary in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


class TestJobModel:
    """Tests for Job model."""
    
    def test_job_creation(self, temp_db):
        """Test creating a Job record."""
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            job_type="diffrhythm",
            status="pending",
            prompt="Test prompt",
            metadata={"language": "en", "genre": "lo-fi"}
        )
        temp_db.add(job)
        temp_db.commit()
        
        # Verify persistence
        saved_job = temp_db.query(Job).filter(Job.job_id == job_id).first()
        assert saved_job is not None
        assert saved_job.job_id == job_id
        assert saved_job.job_type == "diffrhythm"
        assert saved_job.status == "pending"
        assert saved_job.prompt == "Test prompt"
        assert saved_job.metadata == {"language": "en", "genre": "lo-fi"}
    
    def test_job_timestamps(self, temp_db):
        """Test that Job timestamps are set correctly."""
        job = Job(job_id=str(uuid.uuid4()), job_type="diffrhythm")
        temp_db.add(job)
        temp_db.commit()
        
        assert job.created_at is not None
        assert job.updated_at is not None
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)
    
    def test_job_default_values(self, temp_db):
        """Test Job model default values."""
        job = Job(job_id=str(uuid.uuid4()))
        temp_db.add(job)
        temp_db.commit()
        
        assert job.status == "pending"
        assert job.progress == 0
        assert job.metadata == {}
        assert job.file_manifest == {}
        assert job.error is None


class TestTrackModel:
    """Tests for Track model."""
    
    def test_track_creation_with_job(self, temp_db):
        """Test creating a Track linked to a Job."""
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job = Job(job_id=job_id, job_type="diffrhythm")
        temp_db.add(job)
        temp_db.commit()
        
        track = Track(
            track_id=track_id,
            job_id=job_id,
            duration=30.5,
            metadata={"artist": "Test Artist", "album": "Test Album"},
            file_path_wav="/path/to/track.wav",
            file_path_mp3="/path/to/track.mp3"
        )
        temp_db.add(track)
        temp_db.commit()
        
        # Verify persistence and relationship
        saved_track = temp_db.query(Track).filter(Track.track_id == track_id).first()
        assert saved_track is not None
        assert saved_track.track_id == track_id
        assert saved_track.job_id == job_id
        assert saved_track.duration == 30.5
        assert saved_track.metadata == {"artist": "Test Artist", "album": "Test Album"}
        assert saved_track.file_path_wav == "/path/to/track.wav"
        assert saved_track.file_path_mp3 == "/path/to/track.mp3"
    
    def test_track_job_relationship(self, temp_db):
        """Test that Track can access related Job."""
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job = Job(job_id=job_id, job_type="diffrhythm", prompt="Test")
        temp_db.add(job)
        temp_db.commit()
        
        track = Track(track_id=track_id, job_id=job_id)
        temp_db.add(track)
        temp_db.commit()
        
        # Access job through track relationship
        saved_track = temp_db.query(Track).filter(Track.track_id == track_id).first()
        assert saved_track.job is not None
        assert saved_track.job.job_id == job_id
        assert saved_track.job.prompt == "Test"


class TestLoopModel:
    """Tests for Loop model."""
    
    def test_loop_creation_with_track(self, temp_db):
        """Test creating a Loop linked to a Track."""
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        loop_id = str(uuid.uuid4())
        
        job = Job(job_id=job_id, job_type="diffrhythm")
        temp_db.add(job)
        temp_db.commit()
        
        track = Track(track_id=track_id, job_id=job_id)
        temp_db.add(track)
        temp_db.commit()
        
        loop = Loop(
            loop_id=loop_id,
            track_id=track_id,
            duration=60,
            fade_in_out=1,
            format="MP3",
            status="PENDING"
        )
        temp_db.add(loop)
        temp_db.commit()
        
        # Verify persistence
        saved_loop = temp_db.query(Loop).filter(Loop.loop_id == loop_id).first()
        assert saved_loop is not None
        assert saved_loop.loop_id == loop_id
        assert saved_loop.track_id == track_id
        assert saved_loop.duration == 60
        assert saved_loop.fade_in_out == 1
        assert saved_loop.format == "MP3"
        assert saved_loop.status == "PENDING"
    
    def test_loop_track_relationship(self, temp_db):
        """Test that Loop can access related Track."""
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        loop_id = str(uuid.uuid4())
        
        job = Job(job_id=job_id, job_type="diffrhythm")
        temp_db.add(job)
        temp_db.commit()
        
        track = Track(track_id=track_id, job_id=job_id, duration=30.0)
        temp_db.add(track)
        temp_db.commit()
        
        loop = Loop(loop_id=loop_id, track_id=track_id, duration=60)
        temp_db.add(loop)
        temp_db.commit()
        
        # Access track through loop relationship
        saved_loop = temp_db.query(Loop).filter(Loop.loop_id == loop_id).first()
        assert saved_loop.track is not None
        assert saved_loop.track.track_id == track_id
        assert saved_loop.track.duration == 30.0


class TestJobRepository:
    """Tests for JobRepository CRUD operations."""
    
    def test_create_job(self, temp_db):
        """Test creating a job through repository."""
        repo = JobRepository(temp_db)
        job_id = str(uuid.uuid4())
        
        job = repo.create(
            job_id=job_id,
            job_type="diffrhythm",
            status="pending",
            prompt="Test prompt",
            metadata={"language": "en"}
        )
        
        assert job.job_id == job_id
        assert job.job_type == "diffrhythm"
        assert job.status == "pending"
    
    def test_get_job_by_id(self, temp_db):
        """Test retrieving a job by ID."""
        repo = JobRepository(temp_db)
        job_id = str(uuid.uuid4())
        
        repo.create(job_id=job_id, job_type="diffrhythm")
        
        job = repo.get_by_id(job_id)
        assert job is not None
        assert job.job_id == job_id
    
    def test_get_nonexistent_job(self, temp_db):
        """Test retrieving a nonexistent job returns None."""
        repo = JobRepository(temp_db)
        job = repo.get_by_id(str(uuid.uuid4()))
        assert job is None
    
    def test_update_job(self, temp_db):
        """Test updating a job."""
        repo = JobRepository(temp_db)
        job_id = str(uuid.uuid4())
        
        repo.create(job_id=job_id, job_type="diffrhythm", status="pending", progress=0)
        
        updated = repo.update(
            job_id=job_id,
            status="completed",
            progress=100,
            file_manifest={"wav": "/path/to/file.wav"}
        )
        
        assert updated is not None
        assert updated.status == "completed"
        assert updated.progress == 100
        assert updated.file_manifest == {"wav": "/path/to/file.wav"}
    
    def test_get_jobs_by_status(self, temp_db):
        """Test retrieving jobs by status."""
        repo = JobRepository(temp_db)
        
        # Create multiple jobs with different statuses
        repo.create(job_id=str(uuid.uuid4()), job_type="diffrhythm", status="pending")
        repo.create(job_id=str(uuid.uuid4()), job_type="diffrhythm", status="pending")
        repo.create(job_id=str(uuid.uuid4()), job_type="diffrhythm", status="completed")
        
        pending_jobs = repo.get_by_status("pending")
        assert len(pending_jobs) == 2
        
        completed_jobs = repo.get_by_status("completed")
        assert len(completed_jobs) == 1
    
    def test_delete_job(self, temp_db):
        """Test deleting a job."""
        repo = JobRepository(temp_db)
        job_id = str(uuid.uuid4())
        
        repo.create(job_id=job_id, job_type="diffrhythm")
        
        result = repo.delete(job_id)
        assert result is True
        
        job = repo.get_by_id(job_id)
        assert job is None


class TestTrackRepository:
    """Tests for TrackRepository CRUD operations."""
    
    def test_create_track(self, temp_db):
        """Test creating a track through repository."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        
        track = track_repo.create(
            track_id=track_id,
            job_id=job_id,
            duration=30.5,
            metadata={"artist": "Test"}
        )
        
        assert track.track_id == track_id
        assert track.job_id == job_id
        assert track.duration == 30.5
    
    def test_get_tracks_by_job_id(self, temp_db):
        """Test retrieving tracks by job ID."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        
        # Create multiple tracks for the same job
        track_repo.create(track_id=str(uuid.uuid4()), job_id=job_id)
        track_repo.create(track_id=str(uuid.uuid4()), job_id=job_id)
        
        tracks = track_repo.get_by_job_id(job_id)
        assert len(tracks) == 2
        assert all(t.job_id == job_id for t in tracks)
    
    def test_update_track(self, temp_db):
        """Test updating a track."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        
        updated = track_repo.update(
            track_id=track_id,
            duration=45.0,
            file_path_wav="/new/path.wav"
        )
        
        assert updated is not None
        assert updated.duration == 45.0
        assert updated.file_path_wav == "/new/path.wav"


class TestLoopRepository:
    """Tests for LoopRepository CRUD operations."""
    
    def test_create_loop(self, temp_db):
        """Test creating a loop through repository."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        loop_repo = LoopRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        loop_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        
        loop = loop_repo.create(
            loop_id=loop_id,
            track_id=track_id,
            duration=120,
            fade_in_out=1,
            format="MP3"
        )
        
        assert loop.loop_id == loop_id
        assert loop.track_id == track_id
        assert loop.duration == 120
    
    def test_get_loops_by_track_id(self, temp_db):
        """Test retrieving loops by track ID."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        loop_repo = LoopRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        
        # Create multiple loops for the same track
        loop_repo.create(loop_id=str(uuid.uuid4()), track_id=track_id, duration=60)
        loop_repo.create(loop_id=str(uuid.uuid4()), track_id=track_id, duration=120)
        
        loops = loop_repo.get_by_track_id(track_id)
        assert len(loops) == 2
        assert all(l.track_id == track_id for l in loops)
    
    def test_get_loops_by_status(self, temp_db):
        """Test retrieving loops by status."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        loop_repo = LoopRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        
        loop_repo.create(loop_id=str(uuid.uuid4()), track_id=track_id, duration=60, status="PENDING")
        loop_repo.create(loop_id=str(uuid.uuid4()), track_id=track_id, duration=120, status="COMPLETED")
        
        pending = loop_repo.get_by_status("PENDING")
        completed = loop_repo.get_by_status("COMPLETED")
        
        assert any(l.track_id == track_id for l in pending)
        assert any(l.track_id == track_id for l in completed)
    
    def test_update_loop(self, temp_db):
        """Test updating a loop."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        loop_repo = LoopRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        loop_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        loop_repo.create(loop_id=loop_id, track_id=track_id, duration=60, status="PENDING")
        
        updated = loop_repo.update(
            loop_id=loop_id,
            status="COMPLETED",
            progress=100,
            result_url="/files/loop123.mp3"
        )
        
        assert updated is not None
        assert updated.status == "COMPLETED"
        assert updated.progress == 100
        assert updated.result_url == "/files/loop123.mp3"


class TestReferentialIntegrity:
    """Tests for referential integrity and cascading deletes."""
    
    def test_track_cascade_delete(self, temp_db):
        """Test that deleting a job also deletes its tracks."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        
        # Delete the job
        job_repo.delete(job_id)
        
        # Track should also be deleted
        track = track_repo.get_by_id(track_id)
        assert track is None
    
    def test_loop_cascade_delete(self, temp_db):
        """Test that deleting a track also deletes its loops."""
        job_repo = JobRepository(temp_db)
        track_repo = TrackRepository(temp_db)
        loop_repo = LoopRepository(temp_db)
        
        job_id = str(uuid.uuid4())
        track_id = str(uuid.uuid4())
        loop_id = str(uuid.uuid4())
        
        job_repo.create(job_id=job_id, job_type="diffrhythm")
        track_repo.create(track_id=track_id, job_id=job_id)
        loop_repo.create(loop_id=loop_id, track_id=track_id, duration=60)
        
        # Delete the track
        track_repo.delete(track_id)
        
        # Loop should also be deleted
        loop = loop_repo.get_by_id(loop_id)
        assert loop is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
