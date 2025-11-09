"""
MusicGen service for AI music generation
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import torch
import soundfile as sf
from transformers import MusicgenForConditionalGeneration, AutoProcessor

logger = logging.getLogger(__name__)


class MusicGenService:
    """
    Service for managing MusicGen AI music generation model
    """
    
    def __init__(self):
        self._model = None
        self._processor = None
        self._device = None
        self._initialization_lock = asyncio.Lock()
        self._track_registry: Dict[str, Dict] = {}
        
        # Paths
        self.model_cache_dir = Path(__file__).parent.parent.parent / "models" / "cache"
        self.output_dir = Path(__file__).parent.parent.parent.parent / "output"
        
        # Model configuration
        self.model_name = "facebook/musicgen-small"
        self.min_duration = 5
        self.max_duration = 60
    
    def _detect_device(self) -> str:
        """
        Automatically detect the best available device
        Priority: CUDA > MPS > CPU
        """
        if torch.cuda.is_available():
            device = "cuda"
            logger.info("CUDA device detected and selected")
        elif torch.backends.mps.is_available():
            device = "mps"
            logger.info("MPS device detected and selected")
        else:
            device = "cpu"
            logger.info("No GPU detected, using CPU")
        
        logger.info(f"Selected device: {device}")
        return device
    
    async def initialize(self) -> None:
        """
        Initialize the MusicGen model
        Loads the model once with async lock protection
        """
        async with self._initialization_lock:
            if self._model is not None:
                logger.info("Model already initialized")
                return
            
            logger.info("Initializing MusicGen model...")
            
            # Create directories if they don't exist
            self.model_cache_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Detect device
            self._device = self._detect_device()
            
            try:
                # Load model and processor in thread to avoid blocking event loop
                self._model, self._processor = await asyncio.to_thread(
                    self._load_model,
                    self.model_name,
                    str(self.model_cache_dir)
                )
                logger.info("MusicGen model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MusicGen model: {e}")
                raise
    
    def _load_model(self, model_name: str, cache_dir: str) -> Tuple[MusicgenForConditionalGeneration, AutoProcessor]:
        """
        Load the MusicGen model using transformers
        """
        logger.info(f"Loading model {model_name} from cache directory {cache_dir}")
        
        # Load the model and processor
        model = MusicgenForConditionalGeneration.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float16 if self._device == "cuda" else torch.float32
        )
        
        processor = AutoProcessor.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        
        # Move to device
        model = model.to(self._device)
        
        logger.info("MusicGen model and processor loaded successfully")
        return model, processor
    
    async def generate(self, prompt: str, duration: int, guidance_scale: float = 3.0, 
                   temperature: float = 1.0, top_k: int = 250, top_p: float = 0.9) -> Dict:
        """
        Generate audio using MusicGen model
        
        Args:
            prompt: Text prompt for generation
            duration: Duration in seconds (5-60)
            guidance_scale: Guidance scale for generation (1.0-15.0)
            temperature: Temperature for generation (0.1-2.0)
            top_k: Top-k sampling parameter (50-500)
            top_p: Top-p sampling parameter (0.0-1.0)
            
        Returns:
            Dictionary containing track metadata and generation info
        """
        if self._model is None or self._processor is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")
        
        # Validate parameters
        if not self.min_duration <= duration <= self.max_duration:
            raise ValueError(f"Duration must be between {self.min_duration} and {self.max_duration} seconds")
        
        if not 1.0 <= guidance_scale <= 15.0:
            raise ValueError("Guidance scale must be between 1.0 and 15.0")
        
        if not 0.1 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.1 and 2.0")
        
        if not 50 <= top_k <= 500:
            raise ValueError("Top-k must be between 50 and 500")
        
        if not 0.0 <= top_p <= 1.0:
            raise ValueError("Top-p must be between 0.0 and 1.0")
        
        # Generate track ID
        track_id = str(uuid.uuid4())
        
        # Create metadata entry
        metadata = {
            "track_id": track_id,
            "prompt": prompt,
            "duration": duration,
            "guidance_scale": guidance_scale,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "device": self._device,
            "created_at": datetime.utcnow().isoformat(),
            "status": "generating",
            "wav_path": None,
            "sample_rate": None,
            "error": None
        }
        
        self._track_registry[track_id] = metadata
        
        try:
            logger.info(f"Generating track {track_id} with prompt: '{prompt}', duration: {duration}s")
            
            # Run generation in thread to avoid blocking event loop
            waveform, sample_rate = await asyncio.to_thread(
                self._generate_audio,
                prompt,
                duration,
                guidance_scale,
                temperature,
                top_k,
                top_p
            )
            
            # Save to file
            wav_filename = f"{track_id}.wav"
            wav_path = self.output_dir / wav_filename
            
            await asyncio.to_thread(
                self._save_wav,
                waveform,
                sample_rate,
                wav_path
            )
            
            # Update metadata
            metadata.update({
                "status": "completed",
                "wav_path": str(wav_path),
                "sample_rate": sample_rate,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Track {track_id} generated successfully: {wav_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate track {track_id}: {e}")
            metadata.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            })
            raise
        
        return metadata
    
    def _generate_audio(self, prompt: str, duration: int, guidance_scale: float, 
                     temperature: float, top_k: int, top_p: float) -> Tuple[np.ndarray, int]:
        """
        Generate audio waveform using the loaded MusicGen model
        """
        # MusicGen generates at 32kHz by default
        target_sample_rate = 32000
        
        # Calculate max tokens based on duration (MusicGen uses ~12.5 tokens per second)
        max_new_tokens = int(duration * 12.5)
        
        # Process the prompt
        inputs = self._processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        )
        
        # Move inputs to device
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        
        # Generate audio
        with torch.no_grad():
            audio_values = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                guidance_scale=guidance_scale,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
            )
            
            # Extract audio and convert to numpy
            audio = audio_values[0, 0].cpu().numpy()
            
            return audio, target_sample_rate
    
    def _save_wav(self, waveform: np.ndarray, sample_rate: int, wav_path: Path) -> None:
        """
        Save waveform as WAV file
        """
        # Ensure waveform is float32 and in proper range
        waveform = waveform.astype(np.float32)
        
        # Save using soundfile
        sf.write(str(wav_path), waveform, sample_rate)
        logger.info(f"Saved WAV file: {wav_path}")
    
    def get_track(self, track_id: str) -> Optional[Dict]:
        """
        Retrieve metadata for a specific track
        """
        return self._track_registry.get(track_id)
    
    def list_tracks(self) -> Dict[str, Dict]:
        """
        List all tracks in the registry
        """
        return self._track_registry.copy()
    
    async def cleanup_track(self, track_id: str) -> bool:
        """
        Clean up track data (remove from registry and optionally delete file)
        """
        if track_id not in self._track_registry:
            return False
        
        metadata = self._track_registry[track_id]
        
        # Optionally delete the file
        if metadata.get("wav_path") and os.path.exists(metadata["wav_path"]):
            try:
                os.remove(metadata["wav_path"])
                logger.info(f"Deleted WAV file: {metadata['wav_path']}")
            except Exception as e:
                logger.warning(f"Failed to delete WAV file {metadata['wav_path']}: {e}")
        
        # Remove from registry
        del self._track_registry[track_id]
        return True


# Global service instance
_musicgen_service = MusicGenService()


def get_musicgen_service() -> MusicGenService:
    """
    Get the global MusicGen service instance
    """
    return _musicgen_service