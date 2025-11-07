# Implementation Guide - MusicGen Local

Technical architecture and setup for developers working on the MusicGen Local MVP.

## 🏗️ Architecture Overview

**Tech Stack:**
- **Frontend**: React 19 + Vite + TypeScript (port 3000)
- **Backend**: Python FastAPI 0.100+ (port 8000)
- **Queue**: Redis for job persistence (port 6379)
- **AI Engine**: DiffRhythm model (3.2GB, HuggingFace)
- **Storage**: SQLite for metadata, local filesystem for audio files

**Note:** Node.js is used for frontend development (npm, Vite) and for some backend services. The main AI backend runs on Python FastAPI.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐
│   React SPA     │    │  Python FastAPI │    │   Redis     │
│   (port 3000)   │◄──►│   (port 8000)   │◄──►│  (6379)     │
│                 │    │                 │    │             │
│ • UI Screens    │    │ • REST API      │    │ • Job Queue │
│ • API Client    │    │ • DiffRhythm AI │    │ • Progress  │
│ • Routing       │    │ • Audio Loops   │    │             │
│                 │    │ • SQLite DB     │    │             │
└─────────────────┘    └─────────────────┘    └─────────────┘
```

## 🚀 Quick Setup

### Prerequisites
- **Python 3.9+** (backend runtime)
- **Node.js 16+** (frontend dev and some backend services)
- **Redis 7+** (job queue)
- **FFmpeg** (audio processing)
- **GPU recommended** (NVIDIA CUDA or Apple Silicon MPS)
- **10GB+ disk space** (for AI models)

### Local Development

```bash
# 1. Environment setup
cp .env.example .env

# 2. Backend setup (Python)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup (npm for development only)
npm install

# 4. Start services (3 terminals)
# Terminal 1 - Redis
redis-server

# Terminal 2 - Python backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 - Frontend dev server
npm run dev
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

## 🐍 Python Backend (FastAPI)

### Project Structure

```
python/
├── main.py                 # FastAPI app entry point
├── api/
│   ├── generate.py         # POST /api/generate - Music generation
│   ├── loop.py             # POST /api/loop/jobs - Audio looping
│   └── metadata.py         # GET/PUT /api/tracks - Metadata CRUD
├── models/
│   ├── schemas.py          # Pydantic models
│   └── database.py         # SQLite connection
├── services/
│   ├── diffrhythm.py       # DiffRhythm AI engine
│   ├── audio_loop.py       # Audio loop creator
│   └── storage.py          # File management
├── utils/
│   ├── audio.py            # Audio processing utilities
│   └── redis_client.py     # Redis job queue
└── tests/
    ├── test_api.py
    └── test_audio.py
```

### Key API Endpoints

**Generate Music**
```http
POST /api/generate
Content-Type: application/json

{
  "model": "DiffRhythm",
  "prompt": "Lo-fi hip hop with rain sounds",
  "duration": 180,
  "parameters": {
    "genre": "Electronic",
    "mood": "Relaxed"
  }
}

Response: 200 OK
{
  "job_id": "abc123",
  "status": "pending"
}
```

**Create Audio Loop**
```http
POST /api/loop/jobs
Content-Type: application/json

{
  "trackId": "track-123",
  "duration": 3600,
  "fadeInOut": true,
  "format": "mp3"
}

Response: 202 Accepted
{
  "id": "loop-456",
  "status": "PENDING",
  "progress": 0
}
```

**Get Loop Status**
```http
GET /api/loop/jobs/{jobId}

Response: 200 OK
{
  "id": "loop-456",
  "status": "COMPLETED",
  "progress": 100,
  "resultUrl": "/output/loop_track-123.mp3",
  "duration": 3600
}
```

### DiffRhythm AI Engine

```python
# python/services/diffrhythm.py
from diffusers import DiffusionPipeline
import torch

class DiffRhythmGenerator:
    def __init__(self):
        self.model_name = "ASLP-lab/DiffRhythm-full"
        self.cache_dir = "./models/cache"
        self.device = self._detect_device()
        self.pipeline = None
    
    def _detect_device(self):
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def load_model(self):
        self.pipeline = DiffusionPipeline.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        self.pipeline.to(self.device)
    
    def generate(self, prompt: str, duration: int = 180):
        # Generate audio and return file path
        audio = self.pipeline(prompt, num_inference_steps=50).audio
        output_path = f"./output/{uuid.uuid4()}.mp3"
        # Save audio to file
        return output_path
```

## ⚛️ React Frontend (Vite)

### Project Structure

```
src/
├── App.tsx                 # Main app with routing
├── screens/
│   ├── ModelSelectionScreen.tsx
│   ├── DiffRhythmGeneratorScreen.tsx
│   ├── ExportScreen.tsx
│   └── MetadataEditorScreen.tsx
├── components/
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── ProgressBar.tsx
│   └── MetadataEditorModal.tsx
├── services/
│   ├── api.ts              # Axios HTTP client
│   └── loopService.ts      # Loop job polling
└── types.ts                # TypeScript definitions
```

### Frontend Build & Serve

**Development:**
```bash
npm run dev  # Vite dev server on port 3000
```

**Production:**
```bash
npm run build  # Outputs to dist/
# Serve dist/ with Python:
python -m http.server 3000 --directory dist
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
- GPU/CPU utilization
- Memory usage patterns
- Error rates by model

### Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: OpenTelemetry (planned)

## 📦 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup.

**Environment Variables:**
```bash
# Python Backend
MODEL_CACHE_DIR=/app/models/cache
CUDA_VISIBLE_DEVICES=0  # GPU mode
REDIS_URL=redis://localhost:6379
MAX_CONCURRENT_JOBS=3
JOB_TIMEOUT=600

# Frontend Build (for production static serving)
VITE_API_URL=http://localhost:8000
```

## 🔒 Security

- API keys in environment variables only
- File upload size limits (max 100MB)
- Input validation with Pydantic
- Rate limiting on generation endpoints
- CORS configured for frontend access

## 🛠️ Development Workflow

### Feature Development
1. Create feature branch from main
2. Implement backend endpoints first
3. Add corresponding frontend UI
4. Write tests for both layers
5. Update documentation
6. Submit pull request

### Code Quality
- **Linting**: ESLint (frontend), Black (backend)
- **Type checking**: TypeScript, mypy
- **Testing**: Jest (frontend), pytest (backend)
- **Pre-commit hooks**: Automated formatting and linting

### Git Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9
  
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.10.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
        additional_dependencies:
          - eslint@8.10.0
          - "@typescript-eslint/eslint-plugin"
          - "@typescript-eslint/parser"
```

## 📚 API Documentation

### Auto-generated Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Schema Definitions
```python
# Track metadata schema
class TrackMetadata(BaseModel):
    id: str
    title: str
    artist: str
    genre: str
    duration: int
    created_at: datetime
    file_url: str
    model_used: str
    generation_prompt: str
```

## 🔄 Migration Guide

### From v1 to v2
1. **Database schema updates**: Use Alembic migrations
2. **API changes**: Version endpoints (`/api/v1/`, `/api/v2/`)
3. **Frontend compatibility**: Feature flags for gradual rollout

### Data Backup
```bash
# SQLite backup
cp musicgen.db musicgen_backup_$(date +%Y%m%d).db

# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb redis_backup_$(date +%Y%m%d).rdb
```

## 🚀 Performance Optimization

### Model Optimization
- **Quantization**: Reduce model size with minimal quality loss
- **Batch processing**: Queue multiple generations for efficiency
- **Caching**: Store frequently generated prompts

### Database Optimization
- **Indexing**: Add indexes to frequently queried columns
- **Connection pooling**: Reuse database connections
- **Query optimization**: Use EXPLAIN QUERY PLAN for slow queries

### Frontend Optimization
- **Code splitting**: Load components on demand
- **Image optimization**: WebP format with fallbacks
- **Caching strategy**: Service workers for offline support

## 🔍 Debugging

### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile generation time
import time
start_time = time.time()
# ... generation code ...
print(f"Generation took: {time.time() - start_time:.2f}s")
```

### Frontend Debugging
```typescript
// Enable React DevTools
// Use Redux DevTools for state debugging
// Network tab for API calls
```

### Common Issues
1. **Model loading failures**: Check disk space and network
2. **GPU memory errors**: Reduce batch size or model precision
3. **Redis connection drops**: Check Redis server status
4. **Audio file corruption**: Verify FFmpeg installation

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load balancer**: Nginx or HAProxy
- **Multiple AI workers**: Distribute generation load
- **Database sharding**: Split data across multiple instances

### Vertical Scaling
- **GPU upgrades**: More VRAM for larger models
- **Memory optimization**: Profile and reduce memory usage
- **CPU optimization**: Use multiprocessing for CPU-bound tasks

## 🎯 Future Enhancements

### AI Models
- **Additional models**: MusicGen, AudioLDM, Riffusion
- **Model fine-tuning**: Custom training on user data
- **Ensemble generation**: Combine multiple models

### Features
- **Real-time collaboration**: Multiple users working together
- **Advanced editing**: Waveform editing, effects processing
- **Social features**: Sharing, playlists, community

### Infrastructure
- **Cloud deployment**: AWS, GCP, Azure support
- **Edge computing**: Model inference at the edge
- **Serverless**: Function-as-a-Service for burst workloads