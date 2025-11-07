"""
Comprehensive tests for job queue service
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import Base, get_db
from app.models.job import Job, JobStatus
from app.services.job_queue import JobQueueService


@pytest.fixture
def test_db():
    """Create test database"""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def job_queue_service(test_db):
    """Create job queue service with test database"""
    return JobQueueService(db=test_db)


class TestJobQueueService:
    """Test job queue service functionality"""
    
    def test_enqueue_job(self, job_queue_service):
        """Test job enqueuing"""
        job_id = job_queue_service.enqueue_job(
            job_type="test",
            request_data={"prompt": "test prompt", "duration": 30},
            priority=5
        )
        
        assert job_id is not None
        assert isinstance(job_id, str)
        
        # Verify job was created
        job = job_queue_service.get_job(job_id)
        assert job is not None
        assert job.job_type == "test"
        assert job.request_data == {"prompt": "test prompt", "duration": 30}
        assert job.priority == 5
        assert job.status == JobStatus.QUEUED
        assert job.progress == 0
    
    def test_get_job_not_found(self, job_queue_service):
        """Test getting non-existent job"""
        job = job_queue_service.get_job("non-existent-id")
        assert job is None
    
    def test_update_job_status(self, job_queue_service):
        """Test updating job status"""
        # Create job
        job_id = job_queue_service.enqueue_job(
            job_type="test",
            request_data={"test": "data"}
        )
        
        # Update status
        updated = job_queue_service.update_job(
            job_id,
            status=JobStatus.PROCESSING
        )
        
        assert updated is True
        
        # Verify update
        job = job_queue_service.get_job(job_id)
        assert job.status == JobStatus.PROCESSING
        assert job.started_at is not None
    
    def test_update_job_progress(self, job_queue_service):
        """Test updating job progress"""
        # Create job
        job_id = job_queue_service.enqueue_job(
            job_type="test",
            request_data={"test": "data"}
        )
        
        # Update progress
        updated = job_queue_service.update_progress(
            job_id,
            progress=50,
            message="Processing..."
        )
        
        assert updated is True
        
        # Verify update
        job = job_queue_service.get_job(job_id)
        assert job.progress == 50
        assert job.message == "Processing..."
    
    def test_update_job_with_result(self, job_queue_service):
        """Test updating job with completion and result data"""
        # Create job
        job_id = job_queue_service.enqueue_job(
            job_type="test",
            request_data={"test": "data"}
        )
        
        # Update as completed with result
        result_data = {"output_file": "/path/to/output.mp3", "duration": 30.5}
        updated = job_queue_service.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            result_data=result_data
        )
        
        assert updated is True
        
        # Verify update
        job = job_queue_service.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.progress == 100
        assert job.result_data == result_data
        assert job.completed_at is not None
    
    def test_update_job_failed(self, job_queue_service):
        """Test updating job as failed"""
        # Create job
        job_id = job_queue_service.enqueue_job(
            job_type="test",
            request_data={"test": "data"}
        )
        
        # Update as failed
        updated = job_queue_service.update_job(
            job_id,
            status=JobStatus.FAILED,
            error="Something went wrong",
            message="Processing failed"
        )
        
        assert updated is True
        
        # Verify update
        job = job_queue_service.get_job(job_id)
        assert job.status == JobStatus.FAILED
        assert job.error == "Something went wrong"
        assert job.message == "Processing failed"
        assert job.completed_at is not None
    
    def test_list_jobs_all(self, job_queue_service):
        """Test listing all jobs"""
        # Create multiple jobs
        job_ids = []
        for i in range(5):
            job_id = job_queue_service.enqueue_job(
                job_type=f"test_{i}",
                request_data={"index": i}
            )
            job_ids.append(job_id)
        
        # List all jobs
        jobs = job_queue_service.list_jobs()
        assert len(jobs) == 5
        
        # Debug: print the actual order
        job_types = [job.job_type for job in jobs]
        print(f"Actual job order: {job_types}")
        
        # Verify all created jobs are returned (order may vary due to same timestamps)
        job_types = [job.job_type for job in jobs]
        for i in range(5):
            assert f"test_{i}" in job_types
    
    def test_list_jobs_filtered_by_status(self, job_queue_service):
        """Test listing jobs filtered by status"""
        # Create jobs
        job1_id = job_queue_service.enqueue_job("test1", {"data": "1"})
        job2_id = job_queue_service.enqueue_job("test2", {"data": "2"})
        
        # Update one job to processing
        job_queue_service.update_job(job1_id, status=JobStatus.PROCESSING)
        
        # Filter by queued status
        queued_jobs = job_queue_service.list_jobs(status=JobStatus.QUEUED)
        assert len(queued_jobs) == 1
        assert queued_jobs[0].id == job2_id
        
        # Filter by processing status
        processing_jobs = job_queue_service.list_jobs(status=JobStatus.PROCESSING)
        assert len(processing_jobs) == 1
        assert processing_jobs[0].id == job1_id
    
    def test_list_jobs_filtered_by_type(self, job_queue_service):
        """Test listing jobs filtered by type"""
        # Create jobs of different types
        job1_id = job_queue_service.enqueue_job("type1", {"data": "1"})
        job2_id = job_queue_service.enqueue_job("type2", {"data": "2"})
        job3_id = job_queue_service.enqueue_job("type1", {"data": "3"})
        
        # Filter by type1
        type1_jobs = job_queue_service.list_jobs(job_type="type1")
        assert len(type1_jobs) == 2
        
        # Filter by type2
        type2_jobs = job_queue_service.list_jobs(job_type="type2")
        assert len(type2_jobs) == 1
    
    def test_list_jobs_with_pagination(self, job_queue_service):
        """Test listing jobs with pagination"""
        # Create 10 jobs
        for i in range(10):
            job_queue_service.enqueue_job(f"test_{i}", {"index": i})
        
        # Get first page
        page1 = job_queue_service.list_jobs(limit=3, offset=0)
        assert len(page1) == 3
        
        # Get second page
        page2 = job_queue_service.list_jobs(limit=3, offset=3)
        assert len(page2) == 3
        
        # Verify different jobs
        page1_ids = {job.id for job in page1}
        page2_ids = {job.id for job in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    def test_get_next_job(self, job_queue_service):
        """Test getting next available job"""
        # Create jobs with different priorities
        low_id = job_queue_service.enqueue_job("test", {"priority": "low"}, priority=1)
        high_id = job_queue_service.enqueue_job("test", {"priority": "high"}, priority=10)
        medium_id = job_queue_service.enqueue_job("test", {"priority": "medium"}, priority=5)
        
        # Get next job (should be highest priority)
        next_job = job_queue_service.get_next_job(worker_id="worker1")
        assert next_job is not None
        assert next_job.id == high_id
        assert next_job.status == JobStatus.PROCESSING
        assert next_job.worker_id == "worker1"
        
        # Get next job again (should be medium priority)
        next_job = job_queue_service.get_next_job(worker_id="worker2")
        assert next_job is not None
        assert next_job.id == medium_id
        assert next_job.worker_id == "worker2"
    
    def test_get_next_job_by_type(self, job_queue_service):
        """Test getting next job filtered by type"""
        # Create jobs of different types
        diffrhythm_id = job_queue_service.enqueue_job("diffrhythm", {"type": "music"})
        loop_id = job_queue_service.enqueue_job("loop", {"type": "audio"})
        
        # Get next diffrhythm job
        next_job = job_queue_service.get_next_job(job_types=["diffrhythm"])
        assert next_job is not None
        assert next_job.id == diffrhythm_id
        
        # Get next loop job
        next_job = job_queue_service.get_next_job(job_types=["loop"])
        assert next_job is not None
        assert next_job.id == loop_id
    
    def test_get_job_stats(self, job_queue_service):
        """Test getting job statistics"""
        # Create jobs with different statuses
        job1_id = job_queue_service.enqueue_job("test", {"data": "1"})
        job2_id = job_queue_service.enqueue_job("test", {"data": "2"})
        job3_id = job_queue_service.enqueue_job("test", {"data": "3"})
        
        # Update job statuses
        job_queue_service.update_job(job1_id, status=JobStatus.PROCESSING)
        job_queue_service.update_job(job2_id, status=JobStatus.COMPLETED)
        job_queue_service.update_job(job3_id, status=JobStatus.FAILED)
        
        # Get stats
        stats = job_queue_service.get_job_stats()
        
        assert stats["queued"] == 0
        assert stats["processing"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 1
        assert stats["total"] == 3
        assert stats["active"] == 1
    
    def test_cleanup_old_jobs(self, job_queue_service):
        """Test cleaning up old jobs"""
        # Create jobs
        job1_id = job_queue_service.enqueue_job("test", {"data": "1"})
        job2_id = job_queue_service.enqueue_job("test", {"data": "2"})
        
        # Complete one job
        job_queue_service.update_job(job1_id, status=JobStatus.COMPLETED)
        
        # Mock old creation time
        with job_queue_service.get_db_session() as db:
            job = db.query(Job).filter(Job.id == job1_id).first()
            old_time = datetime.now(timezone.utc) - timedelta(days=35)
            job.created_at = old_time
            db.commit()
        
        # Clean up old jobs
        cleaned = job_queue_service.cleanup_old_jobs(days=30)
        assert cleaned == 1
        
        # Verify job was cleaned up
        job = job_queue_service.get_job(job1_id)
        assert job is None
        
        # Verify other job still exists
        job = job_queue_service.get_job(job2_id)
        assert job is not None
    
    def test_job_model_properties(self, job_queue_service):
        """Test Job model properties"""
        # Create job
        job_id = job_queue_service.enqueue_job("test", {"data": "test"})
        job = job_queue_service.get_job(job_id)
        
        # Test initial state
        assert job.is_finished is False
        assert job.is_active is True
        
        # Update to processing
        job_queue_service.update_job(job_id, status=JobStatus.PROCESSING)
        job = job_queue_service.get_job(job_id)
        assert job.is_finished is False
        assert job.is_active is True
        
        # Update to completed
        job_queue_service.update_job(job_id, status=JobStatus.COMPLETED)
        job = job_queue_service.get_job(job_id)
        assert job.is_finished is True
        assert job.is_active is False
        
        # Update to failed
        job_queue_service.update_job(job_id, status=JobStatus.FAILED, error="test error")
        job = job_queue_service.get_job(job_id)
        assert job.is_finished is True
        assert job.is_active is False
    
    def test_job_model_to_dict(self, job_queue_service):
        """Test Job model to_dict method"""
        # Create job with data
        job_id = job_queue_service.enqueue_job(
            "test",
            {"prompt": "test", "duration": 30},
            priority=5
        )
        
        # Update with progress
        job_queue_service.update_job(
            job_id,
            progress=50,
            message="Processing..."
        )
        
        job = job_queue_service.get_job(job_id)
        job_dict = job.to_dict()
        
        # Verify dictionary structure
        expected_keys = [
            "id", "status", "progress", "job_type", "priority",
            "request_data", "result_data", "message", "error",
            "created_at", "updated_at", "started_at", "completed_at", "worker_id"
        ]
        
        for key in expected_keys:
            assert key in job_dict
        
        assert job_dict["job_type"] == "test"
        assert job_dict["priority"] == 5
        assert job_dict["progress"] == 50
        assert job_dict["message"] == "Processing..."
    
    @patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"})
    def test_redis_integration_disabled(self, job_queue_service):
        """Test that Redis integration is disabled when Redis is not available"""
        # Create service with Redis enabled in env but Redis not available
        service = JobQueueService(redis_enabled=True)
        
        assert service.redis_enabled is False
        assert service.redis_client is None


class TestJobQueueServiceWithMockWorker:
    """Test job queue service with mock worker functions"""
    
    def test_background_job_processing_simulation(self, job_queue_service):
        """Simulate background job processing"""
        def mock_worker_function(job_id: str, queue_service: JobQueueService):
            """Mock worker that processes a job"""
            try:
                # Update to processing
                queue_service.update_job(job_id, status=JobStatus.PROCESSING, message="Starting work")
                
                # Simulate work with progress updates
                for progress in range(25, 101, 25):
                    queue_service.update_progress(job_id, progress, f"Working... {progress}%")
                
                # Complete with result
                queue_service.update_job(
                    job_id,
                    status=JobStatus.COMPLETED,
                    result_data={"output": "mock_result.txt"}
                )
                
            except Exception as e:
                queue_service.update_job(
                    job_id,
                    status=JobStatus.FAILED,
                    error=str(e)
                )
        
        # Create job
        job_id = job_queue_service.enqueue_job(
            "mock_job",
            {"input": "test_input"}
        )
        
        # Process job
        mock_worker_function(job_id, job_queue_service)
        
        # Verify results
        job = job_queue_service.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.progress == 100
        assert job.result_data == {"output": "mock_result.txt"}
    
    def test_worker_error_handling(self, job_queue_service):
        """Test worker error handling"""
        def failing_worker(job_id: str, queue_service: JobQueueService):
            """Mock worker that always fails"""
            raise ValueError("Simulated worker error")
        
        # Create job
        job_id = job_queue_service.enqueue_job(
            "failing_job",
            {"input": "test_input"}
        )
        
        # Process job (should fail)
        try:
            failing_worker(job_id, job_queue_service)
        except ValueError:
            pass  # Expected
        
        # Manually mark as failed to simulate error handling
        job_queue_service.update_job(
            job_id,
            status=JobStatus.FAILED,
            error="Simulated worker error"
        )
        
        # Verify failure
        job = job_queue_service.get_job(job_id)
        assert job.status == JobStatus.FAILED
        assert job.error == "Simulated worker error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])