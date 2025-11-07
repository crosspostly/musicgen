#!/usr/bin/env python3
"""
Demo script showing job queue service usage
"""

import asyncio
import time
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from fastapi import FastAPI, BackgroundTasks
from app.main import app
from app.core.database import init_db
from app.services.job_queue import JobQueueService
from app.models.job import JobStatus


# Initialize database
init_db()


# Create a demo endpoint
@app.post("/demo/generate")
async def demo_generate(
    prompt: str,
    duration: int = 30,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Demo generation endpoint using job queue"""
    
    # Create job queue service
    queue_service = JobQueueService()
    
    # Enqueue job
    job_id = queue_service.enqueue_job(
        job_type="demo_generation",
        request_data={"prompt": prompt, "duration": duration},
        priority=5
    )
    
    # Start background processing
    background_tasks.add_task(process_demo_job, job_id, queue_service)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Demo generation started for prompt: {prompt}"
    }


async def process_demo_job(job_id: str, queue_service: JobQueueService):
    """Background task to process demo job"""
    
    try:
        # Update status to processing
        queue_service.update_job(
            job_id,
            status=JobStatus.PROCESSING,
            message="Starting demo generation..."
        )
        
        # Simulate generation steps
        steps = [
            (10, "Loading demo model..."),
            (25, "Processing prompt..."),
            (50, "Generating content..."),
            (75, "Post-processing..."),
            (90, "Finalizing..."),
        ]
        
        for progress, message in steps:
            queue_service.update_progress(job_id, progress, message)
            await asyncio.sleep(1)  # Simulate work
        
        # Complete job
        result_data = {
            "output": f"demo_output_{job_id}.txt",
            "prompt": (queue_service.get_job(job_id).request_data or {}).get("prompt", ""),
            "duration": (queue_service.get_job(job_id).request_data or {}).get("duration", 30),
            "processing_time": "5 seconds",
            "format": "text"
        }
        
        queue_service.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            result_data=result_data,
            message="Demo generation completed successfully"
        )
        
        print(f"✅ Demo job {job_id} completed")
        
    except Exception as e:
        # Mark job as failed
        queue_service.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=str(e),
            message=f"Demo generation failed: {e}"
        )
        
        print(f"❌ Demo job {job_id} failed: {e}")


@app.get("/demo/status")
async def demo_status():
    """Get demo job statistics"""
    queue_service = JobQueueService()
    stats = queue_service.get_job_stats()
    
    return {
        "demo_stats": stats,
        "message": "Job queue service is running",
        "instructions": [
            "POST /demo/generate?prompt=your_prompt - Start a demo generation",
            "GET /demo/status - Get job statistics",
            "GET /api/jobs/{job_id} - Get specific job status",
            "GET /api/jobs/ - List all jobs"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Job Queue Service Demo...")
    print("📖 Available endpoints:")
    print("   POST /demo/generate?prompt=your_prompt - Start demo generation")
    print("   GET /demo/status - Get demo statistics")
    print("   GET /api/jobs/ - List all jobs")
    print("   GET /api/jobs/{job_id} - Get job status")
    print("   GET /health - Health check")
    print()
    print("🌐 Server starting on http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)