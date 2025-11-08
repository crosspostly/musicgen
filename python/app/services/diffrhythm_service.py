"""
DiffRhythm service for AI music generation
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
from diffusers import DiffusionPipeline

logger = logging.getLogger(__name__)


class DiffRhythmService:
    """
    Service for managing DiffRhythm AI music generation model
    """
    
    def __init__(self):
        self._model = None
        self._device = None
        self._initialization_lock = asyncio.Lock()
        self._track_registry: Dict[str, Dict] = {}
        
        # Paths
        self.model_cache_dir = Path(__file__).parent.parent.parent / "models" / "cache"
        self.output_dir = Path(__file__).parent.parent.parent.parent / "output"
        
        # Model configuration
        self.model_name = "ASLP-lab/DiffRhythm-full"
        self.min_duration = 5
        self.max_duration = 300
    
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
        Initialize the DiffRhythm model
        Loads the model once with async lock protection
        """
        async with self._initialization_lock:
            if self._model is not None:
                logger.info("Model already initialized")
                return
            
            logger.info("Initializing DiffRhythm model...")
            
            # Create directories if they don't exist
            self.model_cache_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Detect device
            self._device = self._detect_device()
            
            try:
                # Load model in thread to avoid blocking event loop
                self._model = await asyncio.to_thread(
                    self._load_model,
                    self.model_name,
                    str(self.model_cache_dir)
                )
                logger.info("DiffRhythm model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DiffRhythm model: {e}")
                raise
    
    def _load_model(self, model_name: str, cache_dir: str) -> DiffusionPipeline:
        """
        Load the DiffRhythm model using diffusers
        """
        logger.info(f"Loading model {model_name} from cache directory {cache_dir}")
        
        # Load the diffusion pipeline
        pipeline = DiffusionPipeline.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float16 if self._device == "cuda" else torch.float32
        )
        
        # Move to device
        pipeline = pipeline.to(self._device)
        
        # Enable memory efficient attention if available
        if hasattr(pipeline, "enable_xformers_memory_efficient_attention"):
            try:
                pipeline.enable_xformers_memory_efficient_attention()
                logger.info("Enabled xformers memory efficient attention")
            except Exception as e:
                logger.warning(f"Could not enable xformers memory efficient attention: {e}")
        
        return pipeline
    
    async def generate(self, prompt: str, duration: int) -> Dict:
        """
        Generate audio using DiffRhythm model
        
        Args:
            prompt: Text prompt for generation
            duration: Duration in seconds (5-300)
            
        Returns:
            Dictionary containing track metadata and generation info
        """
        if self._model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")
        
        # Validate duration
        if not self.min_duration <= duration <= self.max_duration:
            raise ValueError(f"Duration must be between {self.min_duration} and {self.max_duration} seconds")
        
        # Generate track ID
        track_id = str(uuid.uuid4())
        
        # Create metadata entry
        metadata = {
            "track_id": track_id,
            "prompt": prompt,
            "duration": duration,
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
                duration
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
    
    def _generate_audio(self, prompt: str, duration: int) -> Tuple[np.ndarray, int]:
        """
        Generate audio waveform using the loaded model
        """
        # Calculate number of samples based on duration
        # DiffRhythm typically generates at 22050 Hz
        target_sample_rate = 22050
        num_samples = int(duration * target_sample_rate)
        
        # Generate audio
        with torch.no_grad():
            result = self._model(
                prompt=prompt,
                num_inference_steps=50,  # Default steps
                audio_length_in_s=duration
            )
            
            # Extract audio from result
            if hasattr(result, "audios"):
                audio = result.audios[0]  # Take first sample
            elif isinstance(result, torch.Tensor):
                audio = result
            else:
                # Fallback for different result formats
                audio = result[0] if isinstance(result, (list, tuple)) else result
            
            # Ensure audio is in the right format
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            
            # Ensure mono and correct shape
            if audio.ndim > 1:
                audio = audio.mean(axis=0)  # Convert to mono
            
            # Resample if necessary
            if audio.shape[0] != num_samples:
                # Simple resampling using interpolation
                audio_np = audio
                indices = np.linspace(0, len(audio_np) - 1, num_samples)
                audio = np.interp(indices, np.arange(len(audio_np)), audio_np)
            
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
_diffrhythm_service = DiffRhythmService()


def get_diffrhythm_service() -> DiffRhythmService:
    """
    Get the global DiffRhythm service instance
    """
    return _diffrhythm_service