# Implementation Guide - MusicGen Local

Technical architecture and setup for developers working on the MusicGen Local MVP.

## 🏗️ Architecture Overview

**Frontend**: React 19 + Vite + TypeScript (port 3000)  
**Backend**: FastAPI + Python 3.8+ (port 8000)  
**Queue**: Redis for job persistence (port 6379)  
**AI Engine**: DiffRhythm model (3.2GB, HuggingFace)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   React     │    │  FastAPI    │    │   Redis     │
│   (3000)    │◄──►│   (8000)    │◄──►│  (6379)     │
│             │    │             │    │             │
│ UI Screens  │    │ AI Engines  │    │ Job Queue   │
│ API Client  │    │ Endpoints   │    │ Persistence │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🚀 Quick Setup

### Prerequisites
- Node.js 16+, Python 3.8+, Redis
- GPU recommended (NVIDIA CUDA or Apple Silicon MPS)
- 5GB+ free disk space

### Local Development
```bash
# 1. Environment setup
cp .env.example .env
# Edit .env with your API keys

# 2. Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup  
npm install

# 4. Start services
redis-server  # Terminal 1
python -m uvicorn backend.main:app --reload  # Terminal 2
npm run dev  # Terminal 3
```

### Docker Development
```bash
docker-compose up --build
```

## 🔧 Key Services

### DiffRhythm AI Engine

**Location**: `backend/ai-engines/diffrhythm/`  
**Model**: ASLP-lab/DiffRhythm-full (3.2GB)  
**Performance**: GPU ~10s/track, CPU ~30-60s/track

```python
# Model Manager
class DiffRhythmModelManager:
    def __init__(self):
        self.model_name = "ASLP-lab/DiffRhythm-full"
        self.cache_dir = "./models/cache"
        self.device = self._detect_device()  # GPU/CPU/MPS
    
    def generate_music(self, prompt: str, duration: int = 180):
        # Returns: audio_url, duration, metadata
```

**API Endpoint**: `POST /api/generate`
```json
{
  "model": "DiffRhythm",
  "prompt": "Lo-fi hip hop with rain sounds",
  "duration": 180,
  "parameters": {
    "genre": "Electronic",
    "mood": "Relaxed"
  }
}
```

### Audio Loop Creator

**Location**: `backend/api/loop_creator.py`  
**Purpose**: Extend tracks to 1-10 hours for YouTube streams  
**Libraries**: `pydub`, `librosa`, `numpy`

```python
class AudioLooper:
    def create_seamless_loop(self, audio_file: str, target_duration: int):
        # 1. Analyze start/end compatibility
        # 2. Find optimal loop points  
        # 3. Apply fade-in/fade-out transitions
        # 4. Generate extended audio file
```

**API Endpoint**: `POST /api/loop/create`
```json
{
  "input_file": "track.mp3",
  "target_duration": "2h",
  "fade_duration": 5,
  "output_format": "mp3"
}
```

### Job Management

**Persistence**: Redis (server) + localStorage (browser)  
**Polling**: 1-second intervals, 10-minute maximum  
**Timeout**: 10 minutes per generation

```python
# Job Schema
{
  "id": "uuid",
  "status": "pending|processing|completed|failed",
  "model": "DiffRhythm",
  "created_at": "2024-01-01T00:00:00Z",
  "result": {
    "audio_url": "/output/track_123.mp3",
    "duration": 180
  }
}
```

## 📁 File Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── api/
│   ├── generate.py         # Music generation endpoints
│   ├── loop_creator.py     # Audio looping endpoints
│   └── metadata.py         # Track metadata endpoints
├── ai-engines/
│   ├── diffrhythm/
│   │   ├── model_manager.py
│   │   └── generator.py
│   └── base_engine.py       # Common AI engine interface
├── models/
│   └── schemas.py          # Pydantic models
├── utils/
│   ├── audio.py            # Audio processing utilities
│   └── storage.py          # File management
└── tests/
    ├── test_generate.py
    └── test_looper.py

frontend/
├── src/
│   ├── App.tsx             # Main app with routing
│   ├── screens/            # UI screens
│   │   ├── ModelSelectionScreen.tsx
│   │   ├── DiffRhythmGeneratorScreen.tsx
│   │   └── MetadataEditorScreen.tsx
│   ├── components/         # Reusable UI components
│   ├── services/           # API client functions
│   └── types.ts            # TypeScript definitions
```

## 🧪 Testing

### Unit Tests
```bash
# Backend
pytest backend/tests/ --cov=backend

# Frontend  
npm test
```

### Mock DiffRhythm (for testing)
```python
# Mock implementation returns white noise
def mock_generate_music(prompt: str, duration: int):
    return {
        "audio_url": "/mock/audio.mp3",
        "duration": duration,
        "model": "DiffRhythm-mock"
    }
```

### Integration Tests
- API endpoint responses
- Job queue operations  
- File upload/download
- Error handling scenarios

## 🚨 Error Handling

### Common Error Types
```python
class MusicGenException(Exception):
    pass

class ModelNotFoundError(MusicGenException):
    # AI model not downloaded/available

class GenerationTimeoutError(MusicGenException):
    # Generation exceeded timeout limit

class InvalidAudioFormatError(MusicGenException):
    # Unsupported audio file format
```

### HTTP Status Codes
- `200`: Success
- `400`: Invalid request parameters
- `404`: Model/job not found
- `429`: Rate limit exceeded
- `500`: Internal server error
- `503`: AI service unavailable

## 🔄 CI/CD Pipeline

### GitHub Actions (planned)
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=backend
  
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
```

## 📊 Performance Monitoring

### Key Metrics
- Generation time per model
- Queue depth and processing time
- Memory/CPU usage during generation
- Error rates by type

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger.info(f"Starting DiffRhythm generation: {prompt}")
logger.error(f"Generation failed: {error}")
```

## 🔐 Security Considerations

- API keys stored in environment variables only
- File upload size limits (max 100MB)
- Input validation and sanitization
- Rate limiting on generation endpoints
- CORS configuration for frontend access

## 🚀 Deployment Tips

### Docker Production
```bash
# Build and run with GPU support
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f ai-service
```

### Environment Variables
```bash
# Required for production
MODEL_CACHE_DIR=/app/models/cache
CUDA_VISIBLE_DEVICES=0  # GPU mode
REDIS_URL=redis://redis:6379
MAX_CONCURRENT_JOBS=3
JOB_TIMEOUT=600
```