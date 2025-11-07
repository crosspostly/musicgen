"""
Tests for job API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.database import init_db


@pytest.fixture(scope="function")
def test_client():
    """Create test client with database"""
    # Initialize test database
    init_db()
    
    # Create test client
    with TestClient(app) as client:
        yield client


class TestJobAPI:
    """Test job API endpoints"""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Job Queue Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "job_stats" in data
        assert "redis_enabled" in data
    
    def test_create_job(self, test_client):
        """Test job creation"""
        job_data = {
            "job_type": "test",
            "request_data": {"prompt": "test prompt", "duration": 30},
            "priority": 5
        }
        
        response = test_client.post("/api/jobs/", json=job_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["job_type"] == "test"
        assert data["priority"] == 5
        assert data["status"] == "queued"
        assert data["progress"] == 0
        assert data["request_data"] == {"prompt": "test prompt", "duration": 30}
    
    def test_create_job_invalid_status(self, test_client):
        """Test job creation with invalid status"""
        job_data = {
            "job_type": "test",
            "request_data": {"test": "data"},
            "status": "invalid_status"
        }
        
        response = test_client.post("/api/jobs/", json=job_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "Invalid status" in data["detail"]
    
    def test_get_job(self, test_client):
        """Test getting job by ID"""
        # Create job first
        job_data = {
            "job_type": "test",
            "request_data": {"prompt": "test"}
        }
        create_response = test_client.post("/api/jobs/", json=job_data)
        job_id = create_response.json()["id"]
        
        # Get job
        response = test_client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == job_id
        assert data["job_type"] == "test"
    
    def test_get_nonexistent_job(self, test_client):
        """Test getting non-existent job"""
        response = test_client.get("/api/jobs/non-existent-id")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_update_job(self, test_client):
        """Test updating job"""
        # Create job
        job_data = {
            "job_type": "test",
            "request_data": {"prompt": "test"}
        }
        create_response = test_client.post("/api/jobs/", json=job_data)
        job_id = create_response.json()["id"]
        
        # Update job
        update_data = {
            "status": "processing",
            "progress": 50,
            "message": "Processing..."
        }
        response = test_client.put(f"/api/jobs/{job_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "processing"
        assert data["progress"] == 50
        assert data["message"] == "Processing..."
    
    def test_update_job_invalid_status(self, test_client):
        """Test updating job with invalid status"""
        # Create job
        job_data = {
            "job_type": "test",
            "request_data": {"prompt": "test"}
        }
        create_response = test_client.post("/api/jobs/", json=job_data)
        job_id = create_response.json()["id"]
        
        # Update with invalid status
        update_data = {"status": "invalid_status"}
        response = test_client.put(f"/api/jobs/{job_id}", json=update_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "Invalid status" in data["detail"]
    
    def test_update_job_progress(self, test_client):
        """Test updating job progress"""
        # Create job
        job_data = {
            "job_type": "test",
            "request_data": {"prompt": "test"}
        }
        create_response = test_client.post("/api/jobs/", json=job_data)
        job_id = create_response.json()["id"]
        
        # Update progress
        response = test_client.post(
            f"/api/jobs/{job_id}/progress",
            params={"progress": 75, "message": "Almost done..."}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["progress"] == 75
        assert data["message"] == "Almost done..."
    
    def test_update_job_progress_invalid_range(self, test_client):
        """Test updating job progress with invalid range"""
        # Create job
        job_data = {
            "job_type": "test",
            "request_data": {"prompt": "test"}
        }
        create_response = test_client.post("/api/jobs/", json=job_data)
        job_id = create_response.json()["id"]
        
        # Update with invalid progress (> 100)
        response = test_client.post(
            f"/api/jobs/{job_id}/progress",
            params={"progress": 150}
        )
        assert response.status_code == 422  # Validation error
        
        # Update with invalid progress (< 0)
        response = test_client.post(
            f"/api/jobs/{job_id}/progress",
            params={"progress": -10}
        )
        assert response.status_code == 422  # Validation error
    
    def test_list_jobs(self, test_client):
        """Test listing jobs"""
        # Create multiple jobs
        for i in range(3):
            job_data = {
                "job_type": f"test_{i}",
                "request_data": {"index": i}
            }
            test_client.post("/api/jobs/", json=job_data)
        
        # List all jobs
        response = test_client.get("/api/jobs/")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["jobs"]) == 3
        assert data["total"] == 3
    
    def test_list_jobs_filtered(self, test_client):
        """Test listing jobs with filters"""
        # Create jobs with different types and statuses
        test_client.post("/api/jobs/", json={
            "job_type": "type1",
            "request_data": {"test": "data1"}
        })
        
        job2_response = test_client.post("/api/jobs/", json={
            "job_type": "type2", 
            "request_data": {"test": "data2"}
        })
        job2_id = job2_response.json()["id"]
        
        # Update one job status
        test_client.put(f"/api/jobs/{job2_id}", json={"status": "processing"})
        
        # Filter by type1
        response = test_client.get("/api/jobs/?job_type=type1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["job_type"] == "type1"
        
        # Filter by processing status
        response = test_client.get("/api/jobs/?status=processing")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["status"] == "processing"
    
    def test_list_jobs_pagination(self, test_client):
        """Test listing jobs with pagination"""
        # Create 5 jobs
        for i in range(5):
            test_client.post("/api/jobs/", json={
                "job_type": "test",
                "request_data": {"index": i}
            })
        
        # Get first page
        response = test_client.get("/api/jobs/?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
        
        # Get second page
        response = test_client.get("/api/jobs/?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 2
    
    def test_get_job_stats(self, test_client):
        """Test getting job statistics"""
        # Create jobs with different statuses
        job1_response = test_client.post("/api/jobs/", json={
            "job_type": "test",
            "request_data": {"data": "1"}
        })
        job1_id = job1_response.json()["id"]
        
        job2_response = test_client.post("/api/jobs/", json={
            "job_type": "test", 
            "request_data": {"data": "2"}
        })
        job2_id = job2_response.json()["id"]
        
        job3_response = test_client.post("/api/jobs/", json={
            "job_type": "test",
            "request_data": {"data": "3"}
        })
        job3_id = job3_response.json()["id"]
        
        # Update statuses
        test_client.put(f"/api/jobs/{job1_id}", json={"status": "processing"})
        test_client.put(f"/api/jobs/{job2_id}", json={"status": "completed"})
        test_client.put(f"/api/jobs/{job3_id}", json={"status": "failed"})
        
        # Get stats
        response = test_client.get("/api/jobs/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["queued"] == 0
        assert data["processing"] == 1
        assert data["completed"] == 1
        assert data["failed"] == 1
        assert data["total"] == 3
        assert data["active"] == 1
    
    def test_get_job_stats_by_type(self, test_client):
        """Test getting job statistics by type"""
        # Create jobs of different types
        test_client.post("/api/jobs/", json={
            "job_type": "type1",
            "request_data": {"data": "1"}
        })
        test_client.post("/api/jobs/", json={
            "job_type": "type2",
            "request_data": {"data": "2"}
        })
        
        # Get stats for type1
        response = test_client.get("/api/jobs/stats/type1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        
        # Get stats for type2
        response = test_client.get("/api/jobs/stats/type2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
    
    def test_delete_completed_job(self, test_client):
        """Test deleting completed job"""
        # Create and complete job
        job_response = test_client.post("/api/jobs/", json={
            "job_type": "test",
            "request_data": {"data": "test"}
        })
        job_id = job_response.json()["id"]
        
        # Complete job
        test_client.put(f"/api/jobs/{job_id}", json={
            "status": "completed",
            "result_data": {"output": "test.txt"}
        })
        
        # Delete job
        response = test_client.delete(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "deleted successfully" in data["message"]
        
        # Verify job is gone
        response = test_client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 404
    
    def test_delete_active_job_fails(self, test_client):
        """Test that deleting active job fails"""
        # Create job
        job_response = test_client.post("/api/jobs/", json={
            "job_type": "test",
            "request_data": {"data": "test"}
        })
        job_id = job_response.json()["id"]
        
        # Try to delete active job
        response = test_client.delete(f"/api/jobs/{job_id}")
        assert response.status_code == 400
        
        data = response.json()
        assert "Cannot delete active job" in data["detail"]
    
    def test_complete_job_lifecycle(self, test_client):
        """Test complete job lifecycle from creation to completion"""
        # 1. Create job
        job_data = {
            "job_type": "lifecycle_test",
            "request_data": {"input": "test_data"},
            "priority": 10
        }
        create_response = test_client.post("/api/jobs/", json=job_data)
        assert create_response.status_code == 200
        job_id = create_response.json()["id"]
        
        # 2. Verify initial state
        response = test_client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        job = response.json()
        assert job["status"] == "queued"
        assert job["progress"] == 0
        
        # 3. Start processing
        response = test_client.put(f"/api/jobs/{job_id}", json={
            "status": "processing",
            "message": "Starting work"
        })
        assert response.status_code == 200
        job = response.json()
        assert job["status"] == "processing"
        assert job["started_at"] is not None
        
        # 4. Update progress
        for progress in [25, 50, 75]:
            response = test_client.post(
                f"/api/jobs/{job_id}/progress",
                params={"progress": progress, "message": f"Progress: {progress}%"}
            )
            assert response.status_code == 200
            job = response.json()
            assert job["progress"] == progress
        
        # 5. Complete job
        response = test_client.put(f"/api/jobs/{job_id}", json={
            "status": "completed",
            "result_data": {"output_file": "/path/to/output.mp3", "duration": 30.5}
        })
        assert response.status_code == 200
        job = response.json()
        assert job["status"] == "completed"
        assert job["progress"] == 100
        assert job["completed_at"] is not None
        assert job["result_data"]["output_file"] == "/path/to/output.mp3"
        
        # 6. Verify job appears in completed stats
        response = test_client.get("/api/jobs/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["completed"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])