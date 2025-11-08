"""
Tests for DiffRhythm service
"""
import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import torch

from app.services.diffrhythm_service import DiffRhythmService, get_diffrhythm_service


class TestDiffRhythmService:
    """Test suite for DiffRhythmService"""
    
    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test"""
        return DiffRhythmService()
    
    @pytest.fixture
    def mock_pipeline(self):
        """Mock DiffusionPipeline"""
        pipeline = MagicMock()
        # Mock the from_pretrained class method
        pipeline.from_pretrained = MagicMock(return_value=pipeline)
        pipeline.to = MagicMock(return_value=pipeline)
        pipeline.enable_xformers_memory_efficient_attention = MagicMock()
        
        # Mock the pipeline call result
        mock_result = MagicMock()
        mock_result.audios = [torch.randn(1, 22050)]  # 1 second of audio at 22kHz
        pipeline.return_value = mock_result
        
        return pipeline
    
    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service._model is None
        assert service._device is None
        assert service._track_registry == {}
        assert service.model_name == "ASLP-lab/DiffRhythm-full"
        assert service.min_duration == 5
        assert service.max_duration == 300
    
    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_device_selection_cuda(self, mock_mps, mock_cuda, service):
        """Test device selection with CUDA available"""
        mock_cuda.return_value = True
        mock_mps.return_value = False
        
        device = service._detect_device()
        assert device == "cuda"
    
    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_device_selection_mps(self, mock_mps, mock_cuda, service):
        """Test device selection with MPS available"""
        mock_cuda.return_value = False
        mock_mps.return_value = True
        
        device = service._detect_device()
        assert device == "mps"
    
    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_device_selection_cpu(self, mock_mps, mock_cuda, service):
        """Test device selection falling back to CPU"""
        mock_cuda.return_value = False
        mock_mps.return_value = False
        
        device = service._detect_device()
        assert device == "cpu"
    
    @pytest.mark.asyncio
    async def test_initialize_creates_directories(self, service, mock_pipeline):
        """Test that initialize() creates necessary directories"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            # Mock directories that don't exist
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                await service.initialize()
                
                # Should be called twice - once for model_cache_dir, once for output_dir
                assert mock_mkdir.call_count == 2
                mock_mkdir.assert_any_call(parents=True, exist_ok=True)
    
    @pytest.mark.asyncio
    async def test_initialize_loads_model_once(self, service, mock_pipeline):
        """Test that initialize() only loads the model once"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            # Mock device detection
            service._detect_device = MagicMock(return_value="cpu")
            
            # Call initialize twice
            await service.initialize()
            await service.initialize()
            
            # Should only call from_pretrained once
            mock_pipeline.from_pretrained.assert_called_once()
            assert service._model is not None
    
    @pytest.mark.asyncio
    async def test_initialize_with_cuda_device(self, service, mock_pipeline):
        """Test initialization with CUDA device"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            service._detect_device = MagicMock(return_value="cuda")
            
            await service.initialize()
            
            # Should use float16 for CUDA
            mock_pipeline.from_pretrained.assert_called_once_with(
                "ASLP-lab/DiffRhythm-full",
                cache_dir=str(service.model_cache_dir),
                torch_dtype=torch.float16
            )
    
    @pytest.mark.asyncio
    async def test_initialize_with_cpu_device(self, service, mock_pipeline):
        """Test initialization with CPU device"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            service._detect_device = MagicMock(return_value="cpu")
            
            await service.initialize()
            
            # Should use float32 for CPU
            mock_pipeline.from_pretrained.assert_called_once_with(
                "ASLP-lab/DiffRhythm-full",
                cache_dir=str(service.model_cache_dir),
                torch_dtype=torch.float32
            )
    
    @pytest.mark.asyncio
    async def test_generate_without_initialization(self, service):
        """Test that generate() fails if model not initialized"""
        with pytest.raises(RuntimeError, match="Model not initialized"):
            await service.generate("test prompt", 30)
    
    @pytest.mark.asyncio
    async def test_generate_invalid_duration(self, service):
        """Test duration validation"""
        service._model = MagicMock()  # Mock initialized model
        
        # Test too short
        with pytest.raises(ValueError, match="Duration must be between 5 and 300"):
            await service.generate("test prompt", 3)
        
        # Test too long
        with pytest.raises(ValueError, match="Duration must be between 5 and 300"):
            await service.generate("test prompt", 400)
    
    @pytest.mark.asyncio
    async def test_generate_success(self, service, mock_pipeline):
        """Test successful audio generation"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            # Initialize service
            service._detect_device = MagicMock(return_value="cpu")
            await service.initialize()
            
            # Mock the save method
            with patch.object(service, '_save_wav') as mock_save:
                result = await service.generate("test prompt", 10)
                
                # Verify result structure
                assert result["track_id"] is not None
                assert result["prompt"] == "test prompt"
                assert result["duration"] == 10
                assert result["device"] == "cpu"
                assert result["status"] == "completed"
                assert result["wav_path"] is not None
                assert result["sample_rate"] == 22050
                assert result["created_at"] is not None
                assert result["completed_at"] is not None
                assert result["error"] is None
                
                # Verify file was saved
                mock_save.assert_called_once()
                
                # Verify track is in registry
                track_id = result["track_id"]
                assert track_id in service._track_registry
                assert service.get_track(track_id) == result
    
    @pytest.mark.asyncio
    async def test_generate_failure(self, service, mock_pipeline):
        """Test generation failure handling"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            # Initialize service
            service._detect_device = MagicMock(return_value="cpu")
            await service.initialize()
            
            # Mock generation to raise an exception
            with patch.object(service, '_generate_audio', side_effect=Exception("Generation failed")):
                with pytest.raises(Exception, match="Generation failed"):
                    await service.generate("test prompt", 10)
                
                # Verify track is marked as failed
                tracks = service.list_tracks()
                assert len(tracks) == 1
                
                track = list(tracks.values())[0]
                assert track["status"] == "failed"
                assert track["error"] == "Generation failed"
                assert track["failed_at"] is not None
    
    def test_generate_audio(self, service, mock_pipeline):
        """Test audio generation method"""
        # Setup mock model
        mock_result = MagicMock()
        mock_audio = torch.randn(1, 44100)  # 2 seconds at 22kHz
        mock_result.audios = [mock_audio]
        service._model = MagicMock(return_value=mock_result)
        
        waveform, sample_rate = service._generate_audio("test prompt", 2)
        
        assert sample_rate == 22050
        assert isinstance(waveform, np.ndarray)
        assert waveform.shape[0] == 44100  # 2 seconds * 22050 Hz
    
    def test_generate_audio_tensor_result(self, service):
        """Test audio generation with tensor result"""
        # Setup mock model returning tensor directly
        mock_audio = torch.randn(1, 22050)  # 1 second at 22kHz
        service._model = MagicMock(return_value=mock_audio)
        
        waveform, sample_rate = service._generate_audio("test prompt", 1)
        
        assert sample_rate == 22050
        assert isinstance(waveform, np.ndarray)
        assert waveform.shape[0] == 22050
    
    def test_generate_audio_mono_conversion(self, service):
        """Test conversion to mono audio"""
        # Setup mock model returning stereo audio
        mock_audio = torch.randn(2, 22050)  # Stereo, 1 second at 22kHz
        service._model = MagicMock(return_value=mock_audio)
        
        waveform, sample_rate = service._generate_audio("test prompt", 1)
        
        assert sample_rate == 22050
        assert isinstance(waveform, np.ndarray)
        assert waveform.shape[0] == 22050  # Should be mono
    
    def test_generate_audio_resampling(self, service):
        """Test audio resampling when needed"""
        # Setup mock model returning wrong length
        mock_audio = torch.randn(1, 16000)  # Wrong length
        service._model = MagicMock(return_value=mock_audio)
        
        waveform, sample_rate = service._generate_audio("test prompt", 1)
        
        assert sample_rate == 22050
        assert waveform.shape[0] == 22050  # Should be resampled to correct length
    
    def test_save_wav(self, service):
        """Test WAV file saving"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            wav_path = Path(temp_dir) / "test.wav"
            
            # Create test waveform
            waveform = np.random.randn(22050).astype(np.float32)  # 1 second
            sample_rate = 22050
            
            # Save the file
            service._save_wav(waveform, sample_rate, wav_path)
            
            # Verify file exists
            assert wav_path.exists()
            assert wav_path.stat().st_size > 0
    
    def test_get_track(self, service):
        """Test track retrieval"""
        # Add a track to registry
        track_id = str(uuid.uuid4())
        track_data = {"track_id": track_id, "status": "test"}
        service._track_registry[track_id] = track_data
        
        # Test existing track
        result = service.get_track(track_id)
        assert result == track_data
        
        # Test non-existent track
        result = service.get_track("non-existent")
        assert result is None
    
    def test_list_tracks(self, service):
        """Test track listing"""
        # Add some tracks
        track1 = {"track_id": "1", "status": "test1"}
        track2 = {"track_id": "2", "status": "test2"}
        service._track_registry["1"] = track1
        service._track_registry["2"] = track2
        
        # Test listing
        result = service.list_tracks()
        assert result == {"1": track1, "2": track2}
        
        # Verify it's a copy
        result["3"] = {"track_id": "3"}
        assert "3" not in service._track_registry
    
    @pytest.mark.asyncio
    async def test_cleanup_track(self, service):
        """Test track cleanup"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Add track to registry
            track_id = str(uuid.uuid4())
            service._track_registry[track_id] = {
                "track_id": track_id,
                "wav_path": temp_path,
                "status": "completed"
            }
            
            # Cleanup track
            result = await service.cleanup_track(track_id)
            
            assert result is True
            assert track_id not in service._track_registry
            assert not os.path.exists(temp_path)
            
        finally:
            # Clean up temp file if it still exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_track(self, service):
        """Test cleanup of non-existent track"""
        result = await service.cleanup_track("non-existent")
        assert result is False
    
    def test_get_diffrhythm_service(self):
        """Test global service getter"""
        service1 = get_diffrhythm_service()
        service2 = get_diffrhythm_service()
        
        # Should return the same instance
        assert service1 is service2
        assert isinstance(service1, DiffRhythmService)
    
    @pytest.mark.asyncio
    async def test_concurrent_initialization(self, service, mock_pipeline):
        """Test that concurrent initialization calls are handled correctly"""
        with patch('app.services.diffrhythm_service.DiffusionPipeline', mock_pipeline):
            service._detect_device = MagicMock(return_value="cpu")
            
            # Run multiple initializations concurrently
            tasks = [service.initialize() for _ in range(5)]
            await asyncio.gather(*tasks)
            
            # Should only call from_pretrained once
            mock_pipeline.from_pretrained.assert_called_once()
            assert service._model is not None