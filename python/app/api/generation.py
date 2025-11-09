"""
Generation API endpoints for direct prompt → track flow
"""

import os
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..dependencies import get_musicgen_service
from ..database import TrackRepository, get_session

router = APIRouter(prefix="/api", tags=["generation"])


class MusicGenRequest(BaseModel):
    """MusicGen generation request model"""
    prompt: str = Field(..., description="Text prompt for generation (in English)", min_length=1)
    duration: int = Field(default=30, ge=5, le=60, description="Duration in seconds (5-60)")
    guidance_scale: float = Field(default=3.0, ge=1.0, le=15.0, description="Guidance scale (1.0-15.0)")
    temperature: float = Field(default=1.0, ge=0.1, le=2.0, description="Temperature (0.1-2.0)")
    top_k: int = Field(default=250, ge=50, le=500, description="Top-K sampling (50-500)")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-P sampling (0.0-1.0)")


class BarkRequest(BaseModel):
    """Bark generation request model"""
    text: str = Field(..., description="Text to generate speech from", max_length=200)
    voice_preset: str = Field(default="v2/ru_speaker_0", description="Voice preset")
    language: str = Field(default="ru", description="Language code")
    text_temp: float = Field(default=0.7, ge=0.1, le=2.0, description="Text temperature")
    waveform_temp: float = Field(default=0.7, ge=0.1, le=2.0, description="Waveform temperature")


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
    request: MusicGenRequest,
):
    """
    Generate a music track using MusicGen from a prompt.
    
    Returns immediately with track metadata and audio URL.
    
    Args:
        request: MusicGen generation request with prompt and parameters
        
    Returns:
        GenerationResponse with track_id, audio_url, and metadata (201 Created)
    """
    try:
        service = get_musicgen_service()
        
        result = await service.generate(
            prompt=request.prompt,
            duration=request.duration,
            guidance_scale=request.guidance_scale,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p
        )
        
        # Create audio URL relative to output directory
        audio_filename = f"{result['track_id']}.wav"
        audio_url = f"/output/{audio_filename}"
        
        return GenerationResponse(
            track_id=result["track_id"],
            audio_url=audio_url,
            duration=result["duration"],
            device=result["device"],
            created_at=result["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/bark", response_model=GenerationResponse, status_code=201)
async def generate_bark(
    request: BarkRequest,
):
    """
    Generate speech using Bark from text.
    
    Returns immediately with track metadata and audio URL.
    
    Args:
        request: Bark generation request with text and voice parameters
        
    Returns:
        GenerationResponse with track_id, audio_url, and metadata (201 Created)
    """
    try:
        # TODO: Implement Bark service when available
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Bark generation not yet implemented"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bark generation failed: {str(e)}"
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
        
        prompt = track.track_metadata.get("prompt", "") if track.track_metadata else ""
        
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
