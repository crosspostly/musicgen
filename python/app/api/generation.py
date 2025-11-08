"""
Generation API endpoints for direct prompt → track flow
"""

import os
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..dependencies import get_diffrhythm_service
from ..database import TrackRepository, get_session

router = APIRouter(prefix="/api", tags=["generation"])


class GenerationRequest(BaseModel):
    """Generation request model"""
    prompt: str = Field(..., description="Text prompt for generation", min_length=1)
    duration: int = Field(default=30, ge=5, le=300, description="Duration in seconds (5-300)")


class GenerationResponse(BaseModel):
    """Generation response model"""
    track_id: str
    audio_url: str
    duration: int
    device: str
    created_at: datetime


class TrackMetadata(BaseModel):
    """Track metadata response"""
    track_id: str
    prompt: str
    duration: Optional[float]
    status: str
    audio_url: Optional[str]
    file_size: Optional[int]
    created_at: datetime


@router.post("/generate", response_model=GenerationResponse, status_code=201)
async def generate_track(
    request: GenerationRequest,
):
    """
    Generate a music track from a prompt.
    
    Returns immediately with track metadata and audio URL.
    
    Args:
        request: Generation request with prompt and optional duration
        
    Returns:
        GenerationResponse with track_id, audio_url, and metadata (201 Created)
    """
    try:
        service = get_diffrhythm_service()
        
        result = await service.generate(
            prompt=request.prompt,
            duration=request.duration
        )
        
        return GenerationResponse(
            track_id=result["track_id"],
            audio_url=result["audio_url"],
            duration=result["duration"],
            device=result["device"],
            created_at=result["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.get("/track/{track_id}", response_model=TrackMetadata)
async def get_track(track_id: str):
    """
    Get track metadata by ID.
    
    Args:
        track_id: Track identifier
        
    Returns:
        TrackMetadata with prompt, duration, status, and audio URL
        
    Raises:
        404: If track not found
    """
    session = get_session()
    try:
        repo = TrackRepository(session)
        track = repo.get_by_id(track_id)
        
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Track {track_id} not found"
            )
        
        file_size = None
        audio_url = None
        
        if track.file_path_mp3:
            if os.path.exists(track.file_path_mp3):
                file_size = os.path.getsize(track.file_path_mp3)
            audio_url = f"/output/{os.path.basename(track.file_path_mp3)}"
        
        prompt = track.metadata.get("prompt", "") if track.metadata else ""
        
        return TrackMetadata(
            track_id=track.track_id,
            prompt=prompt,
            duration=track.duration,
            status="completed",
            audio_url=audio_url,
            file_size=file_size,
            created_at=track.created_at
        )
    finally:
        session.close()
