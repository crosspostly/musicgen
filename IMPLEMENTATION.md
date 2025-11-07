# Implementation Guide - MusicGen Local

Technical architecture and setup for developers working on the MusicGen Local MVP.

## 🏗️ Architecture Overview

**Tech Stack:**
- **Frontend**: React 19 + Vite + TypeScript (port 3000)
- **Backend**: Python FastAPI 0.100+ (port 8000)
- **Queue**: Redis for job persistence (port 6379)
- **AI Engine**: DiffRhythm model (3.2GB, HuggingFace)
- **Storage**: SQLite for metadata, local filesystem for audio files

**Note:** Node.js is ONLY used for frontend development (npm, Vite). The entire backend runs on Python FastAPI.

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
- **Node.js 16+** (frontend dev only - npm/Vite)
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
python -m uvicorn python.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 - Frontend dev server
npm run dev
```

### Docker Development
```bash
docker-compose up --build
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

```bash
# Backend tests (Python)
pytest python/tests/ --cov=python

# Frontend tests (Node.js test runner)
npm test
```

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
