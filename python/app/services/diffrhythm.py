"""
DiffRhythm Generation Service

Provides music generation capabilities with database persistence.
Wraps the DiffRhythm engine for use in FastAPI applications.
"""

import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

import numpy as np
import soundfile as sf
from pydub import AudioSegment

from ..database import (
    JobRepository,
    TrackRepository,
    get_session,
)

logger = logging.getLogger(__name__)


class DiffRhythmGenerator:
    """Mock DiffRhythm generator for demonstration"""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.sample_rate = 44100
        self._model_loaded = False

    async def load_model(self):
        """Load DiffRhythm model asynchronously"""
        if self._model_loaded:
            return

        logger.info(f"Loading DiffRhythm model on {self.device}...")
        await asyncio.sleep(1)
        self._model_loaded = True
        logger.info("DiffRhythm model loaded successfully")

    async def generate_audio(
        self, prompt: str, duration: int
    ) -> np.ndarray:
        """
        Generate audio from prompt using DiffRhythm model

        Args:
            prompt: Text prompt for generation
            duration: Duration in seconds

        Returns:
            Generated audio as numpy array
        """
        await self.load_model()

        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)

        frequency = 440 + np.random.random() * 100
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)

        for i in range(3):
            freq = 220 * (i + 1)
            audio += 0.1 * np.sin(2 * np.pi * freq * t) * np.random.random()

        audio = audio / np.max(np.abs(audio)) * 0.8

        await asyncio.sleep(2)

        return audio


class DiffRhythmService:
    """Main service for music generation with database persistence"""

    def __init__(self, storage_dir: str = "./output", device: str = "cpu"):
        """
        Initialize DiffRhythm service

        Args:
            storage_dir: Directory for storing generated audio files
            device: Device to use for model (cpu or cuda)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.generator = DiffRhythmGenerator(device=device)
        self._initialized = False
        self._initialization_lock = asyncio.Lock()

    async def initialize(self, preload: bool = False) -> None:
        """
        Initialize the DiffRhythm service
        
        Args:
            preload: Whether to preload the model during initialization
        """
        if self._initialized:
            return

        async with self._initialization_lock:
            if self._initialized:
                return
            
            logger.info(f"Initializing DiffRhythm service (device: {self.device}, preload: {preload})")
            
            if preload:
                await self.warm_start()
            
            self._initialized = True
            logger.info("DiffRhythm service initialization completed")

    async def warm_start(self) -> None:
        """
        Warm start the model by loading it without generating audio
        """
        start_time = asyncio.get_event_loop().time()
        
        logger.info(f"Starting model preload on {self.device}...")
        
        try:
            await self.generator.load_model()
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Model preload completed successfully in {elapsed_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Model preload failed: {str(e)}", exc_info=True)
            raise

    async def generate(
        self, prompt: str, duration: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a music track from a prompt and save to database

        Args:
            prompt: Text prompt for generation
            duration: Duration in seconds (5-300)

        Returns:
            Dictionary with track_id, audio_url, duration, device, created_at
        """
        # Ensure service is initialized before generation
        await self.initialize(preload=False)
        
        try:
            job_id = str(uuid.uuid4())
            track_id = str(uuid.uuid4())
            now = datetime.utcnow()

            session = get_session()
            try:
                job_repo = JobRepository(session)
                job_repo.create(
                    job_id=job_id,
                    job_type="diffrhythm",
                    status="pending",
                    prompt=prompt,
                    job_metadata={"duration": duration},
                )
            finally:
                session.close()

            logger.info(f"Generating audio for track {track_id} with prompt: {prompt}")

            audio = await self.generator.generate_audio(prompt, duration)

            wav_path = self.storage_dir / f"{track_id}.wav"
            mp3_path = self.storage_dir / f"{track_id}.mp3"

            sf.write(str(wav_path), audio, self.generator.sample_rate)
            logger.info(f"Saved WAV file to {wav_path}")

            wav_audio = AudioSegment.from_wav(str(wav_path))
            wav_audio.export(str(mp3_path), format="mp3", bitrate="320k")
            logger.info(f"Saved MP3 file to {mp3_path}")

            actual_duration = len(audio) / self.generator.sample_rate

            session = get_session()
            try:
                track_repo = TrackRepository(session)
                track_repo.create(
                    track_id=track_id,
                    job_id=job_id,
                    duration=actual_duration,
                    track_metadata={
                        "prompt": prompt,
                        "language": "en",
                    },
                    file_path_wav=str(wav_path),
                    file_path_mp3=str(mp3_path),
                )

                job_repo = JobRepository(session)
                job_repo.update(
                    job_id,
                    status="completed",
                    progress=100,
                    file_manifest={
                        "track_id": track_id,
                        "wav_path": str(wav_path),
                        "mp3_path": str(mp3_path),
                    },
                )
            finally:
                session.close()

            return {
                "track_id": track_id,
                "audio_url": f"/output/{track_id}.mp3",
                "duration": int(actual_duration),
                "device": self.device,
                "created_at": now,
            }

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}", exc_info=True)
            raise
