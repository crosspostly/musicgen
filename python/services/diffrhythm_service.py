"""
DiffRhythm AI Music Generation Service

FastAPI microservice for generating music using DiffRhythm model.
Supports async job processing with progress tracking and multi-format export.
Includes SQLAlchemy database persistence for jobs, tracks, and loops.
"""

import os
import sys
import uuid
import asyncio
import logging
import hashlib
import time
import traceback
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum

import torch
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for database imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import (
    JobRepository,
    TrackRepository,
    get_session,
    init_database,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility functions for logging
def hash_prompt(prompt: str) -> str:
    """Generate a hash of the prompt for logging (not full text)"""
    return hashlib.md5(prompt.encode()).hexdigest()[:8]

def get_device_info() -> str:
    """Get device information (GPU/CPU)"""
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"

def log_operation(operation: str, job_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log operation with structured information"""
    timestamp = datetime.now().isoformat()
    device = get_device_info()
    log_data = {
        "timestamp": timestamp,
        "operation": operation,
        "job_id": job_id,
        "device": device,
        "status": status,
        **(details or {})
    }
    
    if status == "error":
        logger.error(f"{operation} - {job_id}: {log_data}")
    else:
        logger.info(f"{operation} - {job_id}: {log_data}")

# Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    LOADING_MODEL = "loading_model"
    PREPARING_PROMPT = "preparing_prompt"
    GENERATING_AUDIO = "generating_audio"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"

# Pydantic models
class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for music generation")
    durationSeconds: int = Field(default=30, ge=10, le=300, description="Duration in seconds (10-300)")
    language: str = Field(default="en", regex="^(ru|en)$", description="Language: 'ru' or 'en'")
    genre: Optional[str] = Field(default=None, description="Music genre")
    mood: Optional[str] = Field(default=None, description="Music mood")

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: Optional[str] = None
    error: Optional[str] = None
    result_url: Optional[str] = None
    wav_path: Optional[str] = None
    mp3_path: Optional[str] = None
    duration: Optional[float] = None

class JobInfo(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    message: Optional[str] = None
    error: Optional[str] = None
    request_data: GenerationRequest
    created_at: datetime
    updated_at: datetime
    result_url: Optional[str] = None
    wav_path: Optional[str] = None
    mp3_path: Optional[str] = None
    duration: Optional[float] = None

# DiffRhythm Engine
class DiffRhythmEngine:
    """Singleton DiffRhythm model engine with async processing"""
    
    _instance = None
    _model = None
    _model_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.device = self._detect_device()
            self.model_cache_dir = os.path.expanduser("~/.cache/diffrhythm")
            os.makedirs(self.model_cache_dir, exist_ok=True)
    
    def _detect_device(self) -> str:
        """Detect if CUDA is available, fallback to CPU with warning"""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"CUDA detected, using GPU: {torch.cuda.get_device_name()}")
        else:
            device = "cpu"
            logger.warning("CUDA not available, using CPU (slower generation)")
        return device
    
    async def load_model(self):
        """Load DiffRhythm model asynchronously"""
        if self._model_loaded:
            return
        
        logger.info(f"Loading DiffRhythm model on {self.device}...")
        
        # Simulate model loading - in real implementation, load actual DiffRhythm model
        await asyncio.sleep(2)  # Simulate loading time
        
        # Mock model for now - replace with actual DiffRhythm loading
        self._model = {
            "loaded": True,
            "device": self.device,
            "sample_rate": 44100
        }
        self._model_loaded = True
        logger.info("DiffRhythm model loaded successfully")
    
    async def generate_audio(self, prompt: str, duration: int, language: str = "en", 
                           genre: str = None, mood: str = None, 
                           progress_callback=None) -> np.ndarray:
        """
        Generate audio from prompt using DiffRhythm model
        
        Args:
            prompt: Text prompt for generation
            duration: Duration in seconds
            language: Language code
            genre: Music genre
            mood: Music mood
            progress_callback: Callback for progress updates
            
        Returns:
            Generated audio as numpy array
        """
        if progress_callback:
            progress_callback(25, "Preparing prompt...")
        
        # Simulate prompt preparation
        await asyncio.sleep(1)
        
        if progress_callback:
            progress_callback(50, "Generating audio...")
        
        # Simulate audio generation - replace with actual DiffRhythm generation
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        
        # Generate mock audio (sine wave with some variation)
        t = np.linspace(0, duration, num_samples)
        frequency = 440 + np.random.random() * 100  # Random frequency around A4
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Add some variation to make it more interesting
        for i in range(3):
            freq = 220 * (i + 1)
            audio += 0.1 * np.sin(2 * np.pi * freq * t) * np.random.random()
        
        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        # Simulate generation time
        await asyncio.sleep(3)
        
        if progress_callback:
            progress_callback(90, "Audio generated")
        
        return audio
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_loaded": self._model_loaded,
            "device": self.device,
            "cache_dir": self.model_cache_dir,
            "sample_rate": 44100 if self._model_loaded else None
        }

# Job store for tracking jobs
class JobStore:
    """Database-backed job store using SQLAlchemy"""
    
    def __init__(self):
        self.jobs: Dict[str, JobInfo] = {}  # In-memory cache for performance
    
    def create_job(self, request_data: GenerationRequest) -> str:
        """Create new job in database and return job ID"""
        job_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Save to database
        session = get_session()
        try:
            repo = JobRepository(session)
            repo.create(
                job_id=job_id,
                job_type="diffrhythm",
                status=JobStatus.PENDING.value,
                prompt=request_data.prompt,
                metadata={
                    "durationSeconds": request_data.durationSeconds,
                    "language": request_data.language,
                    "genre": request_data.genre,
                    "mood": request_data.mood,
                }
            )
            logger.info(f"Created job {job_id} in database")
        except Exception as e:
            logger.error(f"Failed to create job in database: {e}")
        finally:
            session.close()
        
        # Keep in-memory cache for quick access
        job = JobInfo(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            request_data=request_data,
            created_at=now,
            updated_at=now
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get job from in-memory cache"""
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, **kwargs):
        """Update job in memory and database"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            job.updated_at = datetime.now()
            
            # Also update in database
            session = get_session()
            try:
                repo = JobRepository(session)
                update_data = {
                    "status": job.status.value if isinstance(job.status, JobStatus) else job.status,
                    "progress": job.progress,
                }
                if job.error:
                    update_data["error"] = job.error
                if job.file_manifest:
                    update_data["file_manifest"] = {
                        "wav_path": job.wav_path,
                        "mp3_path": job.mp3_path,
                    }
                repo.update(job_id, **update_data)
            except Exception as e:
                logger.error(f"Failed to update job in database: {e}")
            finally:
                session.close()

# Audio export utilities
class AudioExporter:
    """Handle audio export to different formats"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_audio(self, audio: np.ndarray, sample_rate: int, job_id: str) -> tuple[str, str]:
        """
        Save audio as WAV and convert to MP3
        
        Returns:
            Tuple of (wav_path, mp3_path)
        """
        # Save as WAV
        wav_path = self.storage_dir / f"{job_id}.wav"
        sf.write(str(wav_path), audio, sample_rate)
        
        # Convert to MP3
        mp3_path = self.storage_dir / f"{job_id}.mp3"
        wav_audio = AudioSegment.from_wav(str(wav_path))
        wav_audio.export(str(mp3_path), format="mp3", bitrate="320k")
        
        return str(wav_path), str(mp3_path)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        stat = path.stat()
        return {
            "file_path": str(path),
            "file_size": stat.st_size,
            "file_url": f"/files/{path.name}",
            "file_name": path.name
        }

# Global instances
engine = DiffRhythmEngine()
job_store = JobStore()
exporter = AudioExporter(os.getenv("STORAGE_DIR", "./output"))

# FastAPI app
app = FastAPI(
    title="DiffRhythm AI Music Generation Service",
    description="Generate music using DiffRhythm model with async processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def process_generation_job(job_id: str, request_data: GenerationRequest):
    """Background task to process generation job"""
    start_time = time.time()
    prompt_hash = hash_prompt(request_data.prompt)
    
    log_operation("process_generation_job", job_id, "start", {
        "prompt_hash": prompt_hash,
        "duration_seconds": request_data.durationSeconds,
        "language": request_data.language,
        "genre": request_data.genre,
        "mood": request_data.mood,
    })
    
    def progress_callback(progress: int, message: str):
        """Update job progress"""
        job_store.update_job(job_id, progress=progress, message=message)
    
    try:
        # Load model
        job_store.update_job(job_id, status=JobStatus.LOADING_MODEL, progress=5, message="Loading model...")
        await engine.load_model()
        
        # Prepare prompt
        job_store.update_job(job_id, status=JobStatus.PREPARING_PROMPT, progress=15, message="Preparing prompt...")
        
        # Generate audio
        job_store.update_job(job_id, status=JobStatus.GENERATING_AUDIO, progress=20, message="Generating audio...")
        audio = await engine.generate_audio(
            prompt=request_data.prompt,
            duration=request_data.durationSeconds,
            language=request_data.language,
            genre=request_data.genre,
            mood=request_data.mood,
            progress_callback=progress_callback
        )
        
        # Export audio
        job_store.update_job(job_id, status=JobStatus.EXPORTING, progress=95, message="Exporting audio...")
        wav_path, mp3_path = exporter.save_audio(audio, 44100, job_id)
        
        # Get audio duration
        duration = len(audio) / 44100
        
        # Save track to database
        session = get_session()
        try:
            track_repo = TrackRepository(session)
            track_id = str(uuid.uuid4())
            track_repo.create(
                track_id=track_id,
                job_id=job_id,
                duration=duration,
                metadata={
                    "prompt": request_data.prompt,
                    "language": request_data.language,
                    "genre": request_data.genre,
                    "mood": request_data.mood,
                },
                file_path_wav=wav_path,
                file_path_mp3=mp3_path
            )
            log_operation("track_creation", job_id, "success", {
                "track_id": track_id,
                "duration": duration,
            })
        except Exception as e:
            log_operation("track_creation", job_id, "error", {
                "error": str(e),
                "exception_type": type(e).__name__,
            })
        finally:
            session.close()
        
        # Update job with results
        job_store.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            message="Generation completed",
            wav_path=wav_path,
            mp3_path=mp3_path,
            duration=duration,
            result_url=f"/result/{job_id}"
        )
        
        elapsed_time = time.time() - start_time
        log_operation("process_generation_job", job_id, "success", {
            "prompt_hash": prompt_hash,
            "duration": elapsed_time,
            "output_duration": duration,
            "status": "completed",
        })
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        log_operation("process_generation_job", job_id, "error", {
            "prompt_hash": prompt_hash,
            "duration": elapsed_time,
            "error": str(e),
            "exception_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        })
        
        job_store.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=str(e),
            message="Generation failed"
        )

# API endpoints
@app.post("/generate", response_model=dict)
async def generate_music(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Start music generation job"""
    
    # Create job
    job_id = job_store.create_job(request)
    
    # Start background processing
    background_tasks.add_task(process_generation_job, job_id, request)
    
    return {
        "job_id": job_id,
        "status": "accepted",
        "message": "Generation job started"
    }

@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and progress"""
    job = job_store.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Add file URLs if completed
    result_url = None
    if job.status == JobStatus.COMPLETED and job.mp3_path:
        result_url = f"/result/{job_id}"
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        error=job.error,
        result_url=result_url,
        wav_path=job.wav_path,
        mp3_path=job.mp3_path,
        duration=job.duration
    )

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    """Get generated audio file"""
    job = job_store.get_job(job_id)
    
    if not job or job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=404, detail="Result not found")
    
    if not job.mp3_path or not os.path.exists(job.mp3_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        job.mp3_path,
        media_type="audio/mpeg",
        filename=f"{job_id}.mp3"
    )

@app.get("/model/info")
async def get_model_info():
    """Get model information"""
    return engine.get_model_info()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": engine._model_loaded,
        "active_jobs": len([j for j in job_store.jobs.values() if j.status in [JobStatus.PENDING, JobStatus.LOADING_MODEL, JobStatus.PREPARING_PROMPT, JobStatus.GENERATING_AUDIO, JobStatus.EXPORTING]])
    }

@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "prompt": job.request_data.prompt
            }
            for job in job_store.jobs.values()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)