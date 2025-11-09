"""
Music Generation Service using MusicGen via Transformers
NO audiocraft dependency - FIXED audio extraction
"""

import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

import torch
import numpy as np
import soundfile as sf
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from pydub import AudioSegment

from ..database import (
    JobRepository,
    TrackRepository,
    get_session,
)

logger = logging.getLogger(__name__)


class MusicGenGenerator:
    """Real MusicGen generator using Transformers"""

    def __init__(self, size: str = "small", device: str = "cpu"):
        self.size = size
        self.device = device
        self.sample_rate = 32000
        self._model = None
        self._processor = None
        self._model_loaded = False

    async def load_model(self):
        if self._model_loaded:
            return

        logger.info(f"Loading MusicGen-{self.size} on {self.device}...")
        
        try:
            model_name = f"facebook/musicgen-{self.size}"
            
            self._processor = await asyncio.to_thread(
                AutoProcessor.from_pretrained, 
                model_name
            )
            
            self._model = await asyncio.to_thread(
                MusicgenForConditionalGeneration.from_pretrained,
                model_name
            )
            
            self._model.to(self.device)
            self._model_loaded = True
            logger.info(f"MusicGen-{self.size} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise

    async def generate_audio(self, prompt: str, duration: int) -> np.ndarray:
        await self.load_model()

        logger.info(f"Generating: '{prompt}', {duration}s")
        
        try:
            inputs = self._processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            max_new_tokens = int(duration * 50)
            
            with torch.no_grad():
                audio_values = await asyncio.to_thread(
                    self._model.generate,
                    **inputs,
                    do_sample=True,
                    guidance_scale=3.0,
                    max_new_tokens=max_new_tokens,
                )
            
            # FIX: Correct audio extraction from MusicGen output
            # MusicGen returns [batch, channels, samples] or [batch, samples]
            audio = audio_values[0].cpu().numpy()
            
            # Convert to mono if multichannel
            if audio.ndim > 1:
                audio = audio.mean(axis=0)
            
            # Normalize audio to prevent clipping
            max_val = np.abs(audio).max()
            if max_val > 0:
                audio = audio / max_val * 0.95
            
            logger.info(f"Generated: shape={audio.shape}, sample_rate={self.sample_rate}, max_amplitude={max_val:.4f}")
            
            # Warning if audio is silent
            if max_val < 0.001:
                logger.warning("Generated audio is nearly silent! Check model output.")
            
            return audio
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise


class DiffRhythmService:
    """Main service for music generation"""

    def __init__(self, storage_dir: str = "./output", device: str = "cpu", model_size: str = "small"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.generator = MusicGenGenerator(size=model_size, device=device)
        self._initialized = False
        self._initialization_lock = asyncio.Lock()

    async def initialize(self, preload: bool = False) -> None:
        if self._initialized:
            return

        async with self._initialization_lock:
            if self._initialized:
                return
            
            logger.info(f"Initializing service (device: {self.device}, preload: {preload})")
            
            if preload:
                await self.warm_start()
            
            self._initialized = True
            logger.info("Service initialized")

    async def warm_start(self) -> None:
        start_time = asyncio.get_event_loop().time()
        logger.info(f"Preloading model on {self.device}...")
        
        try:
            await self.generator.load_model()
            elapsed = asyncio.get_event_loop().time() - start_time
            logger.info(f"Preload completed in {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"Preload failed: {e}", exc_info=True)
            raise

    async def generate(self, prompt: str, duration: int = 30) -> Dict[str, Any]:
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
                    job_metadata={"duration": duration},
                )
            finally:
                session.close()

            logger.info(f"Generating track {track_id}")

            audio = await self.generator.generate_audio(prompt, duration)

            wav_path = self.storage_dir / f"{track_id}.wav"
            mp3_path = self.storage_dir / f"{track_id}.mp3"

            sf.write(str(wav_path), audio, self.generator.sample_rate)
            logger.info(f"Saved WAV: {wav_path}")

            wav_audio = AudioSegment.from_wav(str(wav_path))
            wav_audio.export(str(mp3_path), format="mp3", bitrate="320k")
            logger.info(f"Saved MP3: {mp3_path}")

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
                        "model": f"musicgen-{self.generator.size}",
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
                "model": f"musicgen-{self.generator.size}",
                "created_at": now,
            }

        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise