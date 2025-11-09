"""
MusicGen Generation Service

Provides music generation capabilities using transformers-based MusicGen.
Cross-platform support with simplified dependencies.
"""

import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

import torch
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from transformers import MusicgenForConditionalGeneration, AutoProcessor

from ..database import (
    JobRepository,
    TrackRepository,
    get_session,
)

logger = logging.getLogger(__name__)


class MusicGenGenerator:
    """MusicGen generator using transformers"""

    def __init__(self, device: str = "cpu", model_size: str = "small"):
        self.device = device
        self.model_size = model_size
        self.sample_rate = 32000
        self._model_loaded = False
        self.model = None
        self.processor = None
        
        # Model configurations
        self.model_configs = {
            "small": "facebook/musicgen-small",
            "medium": "facebook/musicgen-medium", 
            "large": "facebook/musicgen-large"
        }

    async def load_model(self):
        """Load MusicGen model asynchronously using transformers"""
        if self._model_loaded:
            return

        model_name = self.model_configs.get(self.model_size, self.model_configs["small"])
        logger.info(f"Loading MusicGen model '{model_name}' on {self.device}...")
        
        try:
            # Load processor and model
            self.processor = AutoProcessor.from_pretrained(model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Move to device
            self.model = self.model.to(self.device)
            
            # Set to eval mode
            self.model.eval()
            
            self._model_loaded = True
            logger.info(f"MusicGen {self.model_size} model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load MusicGen model: {str(e)}", exc_info=True)
            raise

    async def generate_audio(
        self, prompt: str, duration: int
    ) -> np.ndarray:
        """
        Generate audio from prompt using MusicGen model

        Args:
            prompt: Text prompt for generation
            duration: Duration in seconds

        Returns:
            Generated audio as numpy array
        """
        await self.load_model()
        
        if not self._model_loaded or self.model is None or self.processor is None:
            raise RuntimeError("Model not loaded")

        logger.info(f"Generating audio for prompt: '{prompt}' ({duration}s)")
        
        try:
            # Prepare inputs
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Calculate max generation tokens based on duration
            # MusicGen generates at ~50 Hz, so duration * 50 gives approximate token count
            max_new_tokens = int(duration * 50)
            
            # Generate audio
            with torch.no_grad():
                audio_values = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    guidance_scale=3.0,
                    temperature=1.0,
                )
            
            # Convert to numpy array
            audio_array = audio_values.cpu().numpy()[0]
            
            # Ensure correct sample rate
            if audio_array.shape[0] != 1:
                audio_array = audio_array[0]  # Take first channel if multi-channel
            
            logger.info(f"Generated {len(audio_array)} samples of audio")
            return audio_array
            
        except Exception as e:
            logger.error(f"Audio generation failed: {str(e)}", exc_info=True)
            raise


class DiffRhythmService:
    """Main service for music generation with database persistence"""

    def __init__(self, storage_dir: str = "./output", device: str = "cpu", model_size: str = "small"):
        """
        Initialize MusicGen service

        Args:
            storage_dir: Directory for storing generated audio files
            device: Device to use for model (cpu or cuda)
            model_size: Model size (small, medium, large)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.model_size = model_size
        self.generator = MusicGenGenerator(device=device, model_size=model_size)
        self._initialized = False
        self._initialization_lock = asyncio.Lock()

    async def initialize(self, preload: bool = False) -> None:
        """
        Initialize the MusicGen service
        
        Args:
            preload: Whether to preload the model during initialization
        """
        if self._initialized:
            return

        async with self._initialization_lock:
            if self._initialized:
                return
            
            logger.info(f"Initializing MusicGen service (device: {self.device}, model: {self.model_size}, preload: {preload})")
            
            if preload:
                await self.warm_start()
            
            self._initialized = True
            logger.info("MusicGen service initialization completed")

    async def warm_start(self) -> None:
        """
        Warm start the model by loading it without generating audio
        """
        start_time = asyncio.get_event_loop().time()
        
        logger.info(f"Starting MusicGen {self.model_size} model preload on {self.device}...")
        
        try:
            await self.generator.load_model()
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"MusicGen model preload completed successfully in {elapsed_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"MusicGen model preload failed: {str(e)}", exc_info=True)
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
                    job_type="musicgen",
                    status="pending",
                    prompt=prompt,
                    job_metadata={"duration": duration, "model_size": self.model_size},
                )
            finally:
                session.close()

            logger.info(f"Generating audio for track {track_id} with prompt: {prompt}")

            audio = await self.generator.generate_audio(prompt, duration)

            wav_path = self.storage_dir / f"{track_id}.wav"
            mp3_path = self.storage_dir / f"{track_id}.mp3"

            # Save as WAV using soundfile
            sf.write(str(wav_path), audio, self.generator.sample_rate)
            logger.info(f"Saved WAV file to {wav_path}")

            # Convert to MP3 using pydub
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
                        "model_size": self.model_size,
                        "sample_rate": self.generator.sample_rate,
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