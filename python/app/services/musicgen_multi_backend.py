"""
AI-Driven Music Generation: Multi-Model Backend

Now supports multiple cutting-edge models:
- MusicGen (Meta) [facebook/musicgen-small, medium, large]
- DiffRhythm (ASLP-lab, experimental)
- Riffusion (open-source/stable)

Choose the model via API/Frontend dropdown or parameter. Easily extendable to new models (Museformer, MusicGPT, etc)
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

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = [
    "musicgen-small",
    "musicgen-medium",
    "musicgen-large",
    "diffrhythm-base",
    "riffusion"
]

class BaseMusicModel:
    name = "base"
    available = False
    def __init__(self, device: str = "cpu"): self.device = device
    async def load_model(self): raise NotImplementedError
    async def generate_audio(self, prompt: str, duration: int): raise NotImplementedError

class MusicGenModel(BaseMusicModel):
    def __init__(self, size: str, device: str = "cpu"):
        super().__init__(device)
        self.size = size
        self.sample_rate = 32000
        self._model = None
        self._model_loaded = False
        self.name = f"musicgen-{size}"
        self.available = True
    async def load_model(self):
        if self._model_loaded: return
        try:
            from audiocraft.models import MusicGen
            model_ver = f"facebook/musicgen-{self.size}"
            self._model = await asyncio.to_thread(
                MusicGen.get_pretrained, model_ver, device=self.device
            )
            self._model.set_generation_params(duration=30)
            self._model_loaded = True
        except ImportError as e:
            logger.error("audiocraft not installed! Please install with pip install audiocraft")
            raise e
    async def generate_audio(self, prompt: str, duration: int):
        await self.load_model()
        self._model.set_generation_params(duration=duration)
        import torch
        with torch.no_grad():
            wav = await asyncio.to_thread(self._model.generate, [prompt], progress=False)
        audio = wav[0].cpu().numpy()
        if audio.ndim > 1: audio = audio.mean(axis=0)
        return audio

class DiffRhythmModel(BaseMusicModel):
    def __init__(self, size: str = "base", device: str = "cpu"):
        super().__init__(device)
        self.size = size
        self.sample_rate = 44100
        self._model = None
        self._model_loaded = False
        self.name = f"diffrhythm-{size}"
        self.available = True  # optimistic
    async def load_model(self):
        if self._model_loaded: return
        try:
            from diffusers import DiffusionPipeline
            import torch
            pipeline_name = "ASLP-lab/DiffRhythm-base" if self.size == "base" else "ASLP-lab/DiffRhythm-full"
            self._model = await asyncio.to_thread(
                DiffusionPipeline.from_pretrained, pipeline_name, torch_dtype=torch.float32, cache_dir="./models/cache"
            )
            self._model.to(self.device)
            self._model_loaded = True
        except ImportError as e:
            logger.error("diffusers not installed! Please pip install diffusers transformers")
            raise e
    async def generate_audio(self, prompt: str, duration: int):
        await self.load_model()
        with torch.no_grad():
            out = await asyncio.to_thread(self._model, prompt=prompt, num_inference_steps=50, audio_length_in_s=duration)
        if hasattr(out, "audios"): audio = out.audios[0].cpu().numpy()
        else: audio = np.zeros(duration * self.sample_rate)
        if audio.ndim > 1: audio = audio.mean(axis=0)
        return audio

class RiffusionModel(BaseMusicModel):
    def __init__(self, device: str = "cpu"):
        super().__init__(device)
        self.sample_rate = 44100
        self._model = None
        self._model_loaded = False
        self.name = "riffusion"
        self.available = True
    async def load_model(self):
        if self._model_loaded: return
        try:
            from riffusion.pipeline import RiffusionPipeline
            self._model = await asyncio.to_thread(RiffusionPipeline.from_pretrained, "riffusion/riffusion-model-v1")
            self._model_loaded = True
        except ImportError as e:
            logger.error("riffusion python package not installed! See https://github.com/riffusion/riffusion for install.")
            raise e
    async def generate_audio(self, prompt: str, duration: int):
        await self.load_model()
        output = await asyncio.to_thread(self._model, prompt)
        audio = output.audio
        if audio.ndim > 1: audio = audio.mean(axis=0)
        return audio

MODEL_REGISTRY = {
    "musicgen-small": lambda device: MusicGenModel("small", device),
    "musicgen-medium": lambda device: MusicGenModel("medium", device),
    "musicgen-large": lambda device: MusicGenModel("large", device),
    "diffrhythm-base": lambda device: DiffRhythmModel("base", device),
    "riffusion": lambda device: RiffusionModel(device),
}

class MultiAIService:
    def __init__(self, storage_dir: str = "./output", default_model: str = "musicgen-small", device: str = "cpu"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.default_model = default_model
        self.current_model_name = default_model
        self.model: Optional[BaseMusicModel] = None
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
    async def set_model(self, model_name: str):
        if model_name not in MODEL_REGISTRY:
            raise ValueError(f"Model {model_name} is not supported!")
        if self.model and self.model.name == model_name:
            return  # already set
        logger.info(f"Switching to model: {model_name}")
        self.model = MODEL_REGISTRY[model_name](self.device)
    async def initialize(self, preload: bool = False, model_name: Optional[str] = None) -> None:
        if self._initialized:
            return
        async with self._initialization_lock:
            if self._initialized:
                return
            if model_name:
                await self.set_model(model_name)
            else:
                await self.set_model(self.default_model)
            if preload:
                await self.model.load_model()
            self._initialized = True
    async def generate(self, prompt: str, duration: int = 30, model_name: Optional[str] = None):
        await self.initialize(preload=False, model_name=model_name)
        track_id = str(uuid.uuid4())
        now = datetime.utcnow()
        model = self.model
        audio = await model.generate_audio(prompt, duration)
        sample_rate = getattr(model, 'sample_rate', 44100)
        wav_path = self.storage_dir / f"{track_id}.wav"
        mp3_path = self.storage_dir / f"{track_id}.mp3"
        sf.write(str(wav_path), audio, sample_rate)
        logger.info(f"Saved WAV file to {wav_path}")
        wav_audio = AudioSegment.from_wav(str(wav_path))
        wav_audio.export(str(mp3_path), format="mp3", bitrate="320k")
        logger.info(f"Saved MP3 file to {mp3_path}")
        actual_duration = len(audio) / sample_rate
        return {
            "track_id": track_id,
            "audio_url": f"/output/{track_id}.mp3",
            "duration": int(actual_duration),
            "device": self.device,
            "model": model.name,
            "created_at": now,
        }
