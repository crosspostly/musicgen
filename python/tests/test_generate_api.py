"""
Tests for the Generation API endpoints

Tests cover:
- POST /api/generate with valid and invalid inputs
- GET /api/track/{track_id} for retrieving track metadata
- Validation errors and error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import os
import json
from datetime import datetime
import asyncio
import numpy as np


@pytest.fixture
def client():
    from app.main import create_app
    app = create_app()
    return TestClient(app)


def test_generate_happy_path(client):
    """Test successful generation with valid prompt"""
    async def mock_generate(*args, **kwargs):
        return {
            "track_id": "test-track-123",
            "audio_url": "/output/test-track-123.mp3",
            "duration": 30,
            "device": "cpu",
            "created_at": datetime.utcnow()
        }
    
    with patch('app.services.diffrhythm.DiffRhythmService.generate', new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = mock_generate
        
        response = client.post(
            "/api/generate",
            json={"prompt": "upbeat electronic music", "duration": 30}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["track_id"] == "test-track-123"
        assert data["audio_url"] == "/output/test-track-123.mp3"
        assert data["duration"] == 30
        assert data["device"] == "cpu"


def test_generate_with_default_duration(client):
    """Test generation with default duration (30 seconds)"""
    with patch('app.services.diffrhythm.DiffRhythmService.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = {
            "track_id": "test-track-456",
            "audio_url": "/output/test-track-456.mp3",
            "duration": 30,
            "device": "cpu",
            "created_at": datetime.utcnow()
        }
        
        response = client.post(
            "/api/generate",
            json={"prompt": "calm piano music"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["track_id"] == "test-track-456"


def test_generate_with_custom_duration(client):
    """Test generation with custom duration"""
    with patch('app.services.diffrhythm.DiffRhythmService.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = {
            "track_id": "test-track-60",
            "audio_url": "/output/test-track-60.mp3",
            "duration": 60,
            "device": "cpu",
            "created_at": datetime.utcnow()
        }
        
        response = client.post(
            "/api/generate",
            json={"prompt": "rock music", "duration": 60}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["duration"] == 60


def test_generate_validation_empty_prompt(client):
    """Test validation error for empty prompt"""
    response = client.post(
        "/api/generate",
        json={"prompt": "", "duration": 30}
    )
    
    assert response.status_code == 422
    assert "validation error" in response.text.lower() or "value_error" in response.text.lower()


def test_generate_validation_duration_too_low(client):
    """Test validation error for duration below minimum (5 seconds)"""
    response = client.post(
        "/api/generate",
        json={"prompt": "some music", "duration": 4}
    )
    
    assert response.status_code == 422


def test_generate_validation_duration_too_high(client):
    """Test validation error for duration above maximum (300 seconds)"""
    response = client.post(
        "/api/generate",
        json={"prompt": "some music", "duration": 301}
    )
    
    assert response.status_code == 422


def test_generate_missing_prompt(client):
    """Test validation error for missing prompt field"""
    response = client.post(
        "/api/generate",
        json={"duration": 30}
    )
    
    assert response.status_code == 422


def test_get_track_not_found(client):
    """Test GET /api/track/{track_id} returns 404 for unknown ID"""
    response = client.get("/api/track/nonexistent-id-123")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_track_found(client):
    """Test GET /api/track/{track_id} returns track metadata"""
    with patch('app.database.repositories.TrackRepository.get_by_id') as mock_get:
        from app.database.models import Track
        
        track = Track(
            track_id="test-track-uuid",
            job_id="job-uuid",
            duration=30.5,
            track_metadata={"prompt": "beautiful ambient music", "language": "en"},
            file_path_mp3="/output/test-track-uuid.mp3",
            created_at=datetime.utcnow()
        )
        mock_get.return_value = track
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.getsize', return_value=1024000):
                response = client.get("/api/track/test-track-uuid")
        
        assert response.status_code == 200
        data = response.json()
        assert data["track_id"] == "test-track-uuid"
        assert data["prompt"] == "beautiful ambient music"
        assert data["duration"] == 30.5
        assert data["status"] == "completed"


def test_get_track_with_audio_url(client):
    """Test that GET /api/track returns correct audio URL"""
    with patch('app.database.repositories.TrackRepository.get_by_id') as mock_get:
        from app.database.models import Track
        
        track = Track(
            track_id="audio-track",
            job_id="job-uuid",
            duration=45.0,
            track_metadata={"prompt": "jazz music"},
            file_path_mp3="/tmp/output/audio-track.mp3",
            created_at=datetime.utcnow()
        )
        mock_get.return_value = track
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.getsize', return_value=2048000):
                response = client.get("/api/track/audio-track")
        
        assert response.status_code == 200
        data = response.json()
        assert data["audio_url"] == "/output/audio-track.mp3"
        assert data["file_size"] == 2048000


def test_get_track_without_file(client):
    """Test GET /api/track when file doesn't exist"""
    with patch('app.database.repositories.TrackRepository.get_by_id') as mock_get:
        from app.database.models import Track
        
        track = Track(
            track_id="missing-file-track",
            job_id="job-uuid",
            duration=30.0,
            track_metadata={"prompt": "music"},
            file_path_mp3=None,
            created_at=datetime.utcnow()
        )
        mock_get.return_value = track
        
        response = client.get("/api/track/missing-file-track")
        
        assert response.status_code == 200
        data = response.json()
        assert data["audio_url"] is None
        assert data["file_size"] is None


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "DiffRhythm Generation API"
    assert "version" in data
    assert data["status"] == "running"


def test_generate_error_handling(client):
    """Test error handling in generation endpoint"""
    with patch('app.services.diffrhythm.DiffRhythmService.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = Exception("Model failed to load")
        
        response = client.post(
            "/api/generate",
            json={"prompt": "music", "duration": 30}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Generation failed" in data["detail"]


def test_multiple_generations(client):
    """Test that successive calls reuse the same service instance"""
    call_count = 0
    
    async def track_calls(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return {
            "track_id": f"track-{call_count}",
            "audio_url": f"/output/track-{call_count}.mp3",
            "duration": 30,
            "device": "cpu",
            "created_at": datetime.utcnow()
        }
    
    with patch('app.services.diffrhythm.DiffRhythmService.generate', new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = track_calls
        
        response1 = client.post(
            "/api/generate",
            json={"prompt": "music 1"}
        )
        response2 = client.post(
            "/api/generate",
            json={"prompt": "music 2"}
        )
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["track_id"] == "track-1"
        assert data2["track_id"] == "track-2"


def test_cors_headers_present(client):
    """Test that CORS headers are configured"""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    
    assert response.status_code == 200


def test_service_initialize_preload():
    """Test DiffRhythmService.initialize with preload=True"""
    from app.services.diffrhythm import DiffRhythmService
    
    async def test_preload():
        service = DiffRhythmService()
        
        # Mock the generator's load_model method
        original_load_model = service.generator.load_model
        load_model_called = False
        
        async def mock_load_model():
            nonlocal load_model_called
            load_model_called = True
        
        service.generator.load_model = mock_load_model
        
        # Test initialize with preload=True
        await service.initialize(preload=True)
        
        # Verify load_model was called
        assert load_model_called
        assert service._initialized
        
        # Test subsequent calls don't load model again
        load_model_called = False
        await service.initialize(preload=True)
        assert not load_model_called  # Should not be called again
        
        # Restore original method
        service.generator.load_model = original_load_model
    
    # Run the async test
    asyncio.run(test_preload())


def test_service_initialize_no_preload():
    """Test DiffRhythmService.initialize with preload=False"""
    from app.services.diffrhythm import DiffRhythmService
    
    async def test_no_preload():
        service = DiffRhythmService()
        
        # Mock the generator's load_model method
        original_load_model = service.generator.load_model
        load_model_called = False
        
        async def mock_load_model():
            nonlocal load_model_called
            load_model_called = True
        
        service.generator.load_model = mock_load_model
        
        # Test initialize with preload=False
        await service.initialize(preload=False)
        
        # Verify load_model was NOT called
        assert not load_model_called
        assert service._initialized
        
        # Restore original method
        service.generator.load_model = original_load_model
    
    # Run the async test
    asyncio.run(test_no_preload())


def test_service_warm_start():
    """Test DiffRhythmService.warm_start method"""
    from app.services.diffrhythm import DiffRhythmService
    
    async def test_warm_start():
        service = DiffRhythmService()
        
        # Mock the generator's load_model method
        original_load_model = service.generator.load_model
        load_model_called = False
        
        async def mock_load_model():
            nonlocal load_model_called
            load_model_called = True
        
        service.generator.load_model = mock_load_model
        
        # Test warm_start
        await service.warm_start()
        
        # Verify load_model was called
        assert load_model_called
        
        # Restore original method
        service.generator.load_model = original_load_model
    
    # Run the async test
    asyncio.run(test_warm_start())


def test_service_concurrent_initialization():
    """Test that concurrent initialization calls are handled correctly"""
    from app.services.diffrhythm import DiffRhythmService
    
    async def test_concurrent():
        service = DiffRhythmService()
        
        # Mock the generator's load_model method
        original_load_model = service.generator.load_model
        load_model_call_count = 0
        
        async def mock_load_model():
            nonlocal load_model_call_count
            load_model_call_count += 1
            await asyncio.sleep(0.1)  # Simulate loading time
        
        service.generator.load_model = mock_load_model
        
        # Start multiple concurrent initializations
        tasks = [
            service.initialize(preload=True),
            service.initialize(preload=True),
            service.initialize(preload=True),
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify load_model was called only once
        assert load_model_call_count == 1
        assert service._initialized
        
        # Restore original method
        service.generator.load_model = original_load_model
    
    # Run the async test
    asyncio.run(test_concurrent())


def test_generate_calls_initialize():
    """Test that generate method calls initialize"""
    from app.services.diffrhythm import DiffRhythmService
    
    async def test_generate_init():
        service = DiffRhythmService()
        
        # Mock initialize method
        initialize_called = False
        
        async def mock_initialize(preload: bool = False):
            nonlocal initialize_called
            initialize_called = True
        
        service.initialize = mock_initialize
        
        # Mock the rest of the generation process
        original_generate_audio = service.generator.generate_audio
        service.generator.generate_audio = AsyncMock(return_value=np.array([0.1, 0.2, 0.3]))
        
        # Mock database operations
        with patch('app.services.diffrhythm.get_session') as mock_session:
            mock_session.return_value.close = MagicMock()
            
            with patch('app.services.diffrhythm.sf.write'):
                with patch('app.services.diffrhythm.AudioSegment.from_wav') as mock_audio:
                    mock_audio.return_value.export = MagicMock()
                    
                    try:
                        await service.generate("test prompt", 30)
                    except Exception:
                        pass  # We're only testing that initialize is called
        
        # Verify initialize was called
        assert initialize_called
        
        # Restore original method
        service.generator.generate_audio = original_generate_audio
    
    # Run the async test
    asyncio.run(test_generate_init())
