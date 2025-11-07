"""
Example generation API endpoints using job queue service
"""

from typing import Dict, Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..dependencies import get_job_queue_service
from ..services.job_queue import JobQueueService
from ..models.job import JobStatus

router = APIRouter(prefix="/api/generate", tags=["generation"])


class GenerationRequest(BaseModel):
    """Generation request model"""
    prompt: str = Field(..., description="Text prompt for generation")
    duration: int = Field(default=30, ge=10, le=300, description="Duration in seconds")
    model: str = Field(default="diffrhythm", description="Model to use")
    priority: int = Field(default=0, ge=0, le=100, description="Job priority")


class GenerationResponse(BaseModel):
    """Generation response model"""
    job_id: str
    status: str
    message: str


async def process_generation_job(job_id: str, queue_service: JobQueueService):
    """
    Background task to process generation job
    
    Args:
        job_id: Job identifier
        queue_service: Job queue service
    """
    try:
        # Get job details
        job = queue_service.get_job(job_id)
        if not job:
            return
        
        request_data = job.request_data
        
        # Update status to processing
        queue_service.update_job(
            job_id,
            status=JobStatus.PROCESSING,
            message="Starting generation..."
        )
        
        # Simulate generation steps with progress updates
        steps = [
            (10, "Loading model..."),
            (25, "Preparing prompt..."),
            (50, "Generating audio..."),
            (75, "Post-processing..."),
            (90, "Exporting..."),
        ]
        
        for progress, message in steps:
            queue_service.update_progress(job_id, progress, message)
            
            # Simulate processing time
            import asyncio
            await asyncio.sleep(1)
        
        # Complete with mock result
        result_data = {
            "output_file": f"/output/{job_id}.mp3",
            "duration": request_data.get("duration", 30),
            "model": request_data.get("model", "diffrhythm"),
            "prompt": request_data.get("prompt", ""),
            "file_size": 1024000,  # Mock file size
            "format": "mp3"
        }
        
        queue_service.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            result_data=result_data,
            message="Generation completed successfully"
        )
        
    except Exception as e:
        # Mark job as failed
        queue_service.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=str(e),
            message=f"Generation failed: {e}"
        )


@router.post("/{model}", response_model=GenerationResponse)
async def start_generation(
    model: str,
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Start a generation job using specified model
    
    Args:
        model: Model to use for generation
        request: Generation request data
        background_tasks: FastAPI BackgroundTasks
        queue_service: Job queue service
        
    Returns:
        Generation response with job ID
    """
    # Validate model
    supported_models = ["diffrhythm", "yue", "bark", "lyria", "magnet"]
    if model not in supported_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported model: {model}. Supported models: {supported_models}"
        )
    
    # Prepare request data
    request_data = {
        "prompt": request.prompt,
        "duration": request.duration,
        "model": model
    }
    
    # Enqueue job
    job_id = queue_service.enqueue_job(
        job_type=f"{model}_generation",
        request_data=request_data,
        priority=request.priority,
        status=JobStatus.QUEUED
    )
    
    # Start background processing
    background_tasks.add_task(process_generation_job, job_id, queue_service)
    
    return GenerationResponse(
        job_id=job_id,
        status="queued",
        message=f"Generation job started for model {model}"
    )


@router.post("", response_model=GenerationResponse)
async def start_generation_default(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    """
    Start a generation job using default model
    
    Args:
        request: Generation request data
        background_tasks: FastAPI BackgroundTasks
        queue_service: Job queue service
        
    Returns:
        Generation response with job ID
    """
    # Delegate to model-specific endpoint
    return await start_generation(
        request.model,
        request,
        background_tasks,
        queue_service
    )