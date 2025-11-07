"""
Example worker implementation demonstrating job queue usage
"""

import asyncio
import logging
import time
from typing import Optional

from ..services.job_queue import JobQueueService
from ..models.job import JobStatus

logger = logging.getLogger(__name__)


class ExampleWorker:
    """
    Example worker that processes jobs from the queue
    """
    
    def __init__(self, worker_id: str, queue_service: JobQueueService):
        """
        Initialize worker
        
        Args:
            worker_id: Unique worker identifier
            queue_service: Job queue service instance
        """
        self.worker_id = worker_id
        self.queue_service = queue_service
        self.running = False
    
    async def start(self, poll_interval: int = 5):
        """
        Start worker loop
        
        Args:
            poll_interval: Seconds between job queue polls
        """
        self.running = True
        logger.info(f"Worker {self.worker_id} started")
        
        while self.running:
            try:
                # Get next job
                job = self.queue_service.get_next_job(
                    job_types=["example", "test"],
                    worker_id=self.worker_id
                )
                
                if job:
                    logger.info(f"Worker {self.worker_id} processing job {job.id}")
                    await self.process_job(job)
                else:
                    # No jobs available, wait
                    await asyncio.sleep(poll_interval)
                    
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(poll_interval)
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    def stop(self):
        """Stop worker"""
        self.running = False
    
    async def process_job(self, job):
        """
        Process a single job
        
        Args:
            job: Job to process
        """
        try:
            # Simulate job processing with progress updates
            steps = [
                (10, "Initializing..."),
                (25, "Loading resources..."),
                (50, "Processing data..."),
                (75, "Finalizing..."),
                (100, "Completed")
            ]
            
            for progress, message in steps:
                if not self.running:
                    # Worker stopped, put job back to queue
                    self.queue_service.update_job(
                        job.id,
                        status=JobStatus.QUEUED,
                        message="Worker stopped, job requeued"
                    )
                    return
                
                # Update progress
                self.queue_service.update_progress(job.id, progress, message)
                
                # Simulate work
                await asyncio.sleep(1)
            
            # Mark as completed with result
            result_data = {
                "output": f"Processed by {self.worker_id}",
                "processing_time": time.time(),
                "job_data": job.request_data
            }
            
            self.queue_service.update_job(
                job.id,
                status=JobStatus.COMPLETED,
                result_data=result_data
            )
            
            logger.info(f"Worker {self.worker_id} completed job {job.id}")
            
        except Exception as e:
            # Mark job as failed
            self.queue_service.update_job(
                job.id,
                status=JobStatus.FAILED,
                error=str(e),
                message=f"Processing failed: {e}"
            )
            
            logger.error(f"Worker {self.worker_id} failed job {job.id}: {e}")


# Example usage function
async def run_example_workers():
    """
    Example of running multiple workers
    """
    from ..core.database import init_db
    from ..services.job_queue import JobQueueService
    
    # Initialize database
    init_db()
    
    # Create queue service
    queue_service = JobQueueService()
    
    # Create some test jobs
    for i in range(5):
        queue_service.enqueue_job(
            job_type="example",
            request_data={"test_data": f"job_{i}", "index": i},
            priority=i % 3
        )
    
    # Create workers
    workers = []
    for i in range(2):
        worker = ExampleWorker(f"worker_{i}", queue_service)
        workers.append(worker)
    
    # Start workers
    tasks = []
    for worker in workers:
        task = asyncio.create_task(worker.start(poll_interval=1))
        tasks.append(task)
    
    # Let workers process for a while
    await asyncio.sleep(10)
    
    # Stop workers
    for worker in workers:
        worker.stop()
    
    # Wait for workers to finish
    await asyncio.gather(*tasks)
    
    # Print final stats
    stats = queue_service.get_job_stats()
    print(f"Final job stats: {stats}")


if __name__ == "__main__":
    asyncio.run(run_example_workers())