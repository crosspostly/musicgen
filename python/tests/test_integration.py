"""
Simple integration test for job queue service
"""

import asyncio
import os
import sys
import tempfile

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import init_db
from app.services.job_queue import JobQueueService
from app.models.job import JobStatus


async def test_job_queue_integration():
    """Simple integration test"""
    print("🚀 Running job queue integration test...")
    
    # Initialize database
    init_db()
    
    # Create job queue service
    queue_service = JobQueueService()
    
    # Test 1: Create job
    print("✓ Testing job creation...")
    job_id = queue_service.enqueue_job(
        job_type="integration_test",
        request_data={"test": "data", "number": 42},
        priority=5
    )
    assert job_id is not None
    print(f"  Created job: {job_id}")
    
    # Test 2: Get job
    print("✓ Testing job retrieval...")
    job = queue_service.get_job(job_id)
    assert job is not None
    assert job.job_type == "integration_test"
    assert job.request_data["test"] == "data"
    assert job.request_data["number"] == 42
    print(f"  Retrieved job: {job.job_type}")
    
    # Test 3: Update job progress
    print("✓ Testing progress updates...")
    updated = queue_service.update_progress(job_id, 25, "Working on it...")
    assert updated is True
    
    job = queue_service.get_job(job_id)
    assert job.progress == 25
    assert job.message == "Working on it..."
    print(f"  Updated progress: {job.progress}%")
    
    # Test 4: Update job status
    print("✓ Testing status updates...")
    updated = queue_service.update_job(job_id, status=JobStatus.PROCESSING)
    assert updated is True
    
    job = queue_service.get_job(job_id)
    assert job.status == JobStatus.PROCESSING
    assert job.started_at is not None
    print(f"  Updated status: {job.status}")
    
    # Test 5: Complete job
    print("✓ Testing job completion...")
    result_data = {"output": "/path/to/result.txt", "size": 1024}
    updated = queue_service.update_job(
        job_id,
        status=JobStatus.COMPLETED,
        result_data=result_data
    )
    assert updated is True
    
    job = queue_service.get_job(job_id)
    assert job.status == JobStatus.COMPLETED
    assert job.progress == 100
    assert job.result_data == result_data
    assert job.completed_at is not None
    print(f"  Completed job with result: {job.result_data}")
    
    # Test 6: List jobs
    print("✓ Testing job listing...")
    jobs = queue_service.list_jobs()
    assert len(jobs) >= 1
    print(f"  Listed {len(jobs)} jobs")
    
    # Test 7: Get stats
    print("✓ Testing job statistics...")
    stats = queue_service.get_job_stats()
    assert stats["total"] >= 1
    assert stats["completed"] >= 1
    print(f"  Stats: {stats}")
    
    print("🎉 All integration tests passed!")


async def test_background_processing():
    """Test background processing simulation"""
    print("\n🚀 Running background processing test...")
    
    # Initialize database
    init_db()
    
    # Create job queue service
    queue_service = JobQueueService()
    
    # Create job
    job_id = queue_service.enqueue_job(
        job_type="background_test",
        request_data={"input": "test_data"}
    )
    
    # Simulate background processing
    async def process_job():
        try:
            # Update to processing
            queue_service.update_job(job_id, status=JobStatus.PROCESSING, message="Starting...")
            
            # Simulate work with progress
            for progress in range(25, 101, 25):
                queue_service.update_progress(job_id, progress, f"Progress: {progress}%")
                await asyncio.sleep(0.1)  # Small delay
            
            # Complete job
            queue_service.update_job(
                job_id,
                status=JobStatus.COMPLETED,
                result_data={"output": "background_result.txt"}
            )
            
        except Exception as e:
            queue_service.update_job(
                job_id,
                status=JobStatus.FAILED,
                error=str(e)
            )
    
    # Run processing
    await process_job()
    
    # Verify results
    job = queue_service.get_job(job_id)
    assert job.status == JobStatus.COMPLETED
    assert job.progress == 100
    assert job.result_data["output"] == "background_result.txt"
    
    print("✓ Background processing test passed!")


if __name__ == "__main__":
    async def main():
        await test_job_queue_integration()
        await test_background_processing()
        print("\n🎊 All integration tests completed successfully!")
    
    asyncio.run(main())