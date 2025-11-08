# MVP Setup Guide - Complete Developer Instructions

This guide provides complete, step-by-step instructions for setting up the DiffRhythm AI Music Generation MVP on your local machine. Follow these instructions to get a working development environment from a fresh clone.

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 12+, or Ubuntu 20.04+
- **Python**: 3.9+ (3.10+ recommended)
- **Node.js**: 18+ with npm 9+
- **RAM**: 8GB minimum (16GB+ recommended for GPU support)
- **Storage**: 15GB+ free space (for models and generated files)
- **FFmpeg**: Required for audio processing

### Installation Prerequisites

**macOS:**
```bash
brew install python@3.10 node ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.10 python3-pip nodejs npm ffmpeg
```

**Windows:**
- Download Python 3.10+ from https://python.org
- Download Node.js 18+ from https://nodejs.org
- Download FFmpeg from https://ffmpeg.org/download.html or use `winget install ffmpeg`

---

## 🚀 Quick Setup (5-10 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/crosspostly/musicgen
cd musicgen
```

### 2. Copy Environment Configuration

```bash
cp .env.example .env
```

### 3. Run the Development Startup Script

```bash
# Make script executable (Linux/macOS only)
chmod +x start-dev.sh

# Run the automated setup
./start-dev.sh
```

This script handles:
- Creating necessary directories (including `output/` and `python/models/cache/`)
- Installing Node.js dependencies (frontend and backend)
- Creating Python virtual environment
- Installing Python packages
- Starting all three services

**Expected output:**
```
✅ All services started!
=====================
🌐 Frontend:     http://localhost:3000
🔧 Backend:      http://localhost:3001
🐍 Python API:   http://localhost:8000
```

Access the application at: **http://localhost:3000**

---

## 🔧 Manual Setup (if start-dev.sh is unavailable)

### Step 1: Create Required Directories

```bash
mkdir -p output
mkdir -p python/models/cache
mkdir -p storage
mkdir -p temp
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r python/requirements.txt
```

### Step 3: Install Node.js Dependencies

```bash
# Install root dependencies (frontend)
npm install

# Install backend dependencies
cd backend && npm install && cd ..
```

### Step 4: Environment Configuration

Edit `.env` file with your configuration (copy from `.env.example` if needed):

```env
# Service Ports (defaults work for local dev)
PORT=3001

# Python Service Configuration
PY_DIFFRHYTHM_URL=http://localhost:8000
OUTPUT_DIR=./output
TEMP_DIR=./temp

# Model Cache (must exist)
MODEL_CACHE_DIR=./python/models/cache

# Database
DATABASE_PATH=./storage/database.sqlite
STORAGE_DIR=./storage

# GPU Configuration (set to "" for CPU mode)
CUDA_VISIBLE_DEVICES=0

# Performance
MAX_CONCURRENT_JOBS=1
JOB_TIMEOUT=600
```

---

## 🎯 Starting the Services

### Option A: Automated (Recommended)

```bash
./start-dev.sh
```

This starts all three services concurrently with automatic log output.

### Option B: Individual Service Commands

Open 3 separate terminal windows and run:

**Terminal 1 - Python AI Service (port 8000):**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
cd python
python -m app.main
```

Or with explicit uvicorn command:
```bash
source venv/bin/activate
cd python
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Node.js Backend (port 3001):**
```bash
cd backend
npm run dev
```

**Terminal 3 - React Frontend (port 3000/5173):**
```bash
npm run dev
```

**Expected startup output:**
- Frontend: Vite dev server (http://localhost:5173 or http://localhost:3000)
- Backend: Express server listening on port 3001
- Python: FastAPI with Uvicorn on port 8000, model preload starting

### Option C: All Services with npm Script

```bash
npm run dev:full
```

---

## ✅ Verify Installation

After all services are running, verify they're working:

### Health Checks

```bash
# Frontend (should return HTML)
curl http://localhost:3000

# Backend API
curl http://localhost:3001/api/health

# Python AI Service
curl http://localhost:8000/health
```

Expected responses:
```json
{"status": "healthy", ...}
```

### Test API Generation Endpoint

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "relaxing lo-fi beat", "duration": 10}'
```

Expected response (201 Created):
```json
{
  "track_id": "track_123abc...",
  "audio_url": "/output/track_123abc....wav",
  "duration": 10,
  "device": "cpu",
  "created_at": "2024-11-08T12:34:56Z"
}
```

---

## 🎵 API Reference

### Generate Music

**Endpoint:** `POST /api/generate`

**Request:**
```json
{
  "prompt": "lo-fi hip hop beat",
  "duration": 30
}
```

**Parameters:**
- `prompt` (string, required): Music description (min 1 character)
- `duration` (integer, optional): Duration in seconds (default: 30, range: 5-300)

**Response (201 Created):**
```json
{
  "track_id": "unique_track_id",
  "audio_url": "/output/filename.wav",
  "duration": 30,
  "device": "cpu|cuda",
  "created_at": "2024-11-08T12:34:56Z"
}
```

### Get Track Metadata

**Endpoint:** `GET /api/track/{track_id}`

**Response:**
```json
{
  "track_id": "unique_track_id",
  "prompt": "lo-fi hip hop beat",
  "duration": 30,
  "status": "completed",
  "audio_url": "/output/filename.wav",
  "file_size": 245000,
  "created_at": "2024-11-08T12:34:56Z"
}
```

### Static File Serving

Generated audio files are available at:
```
http://localhost:8000/output/{filename}
```

---

## 🤖 AI Model Information

### DiffRhythm Model

The application uses the **DiffRhythm** model for music generation:

- **Model Size**: ~3.2GB
- **Generation Time**: ~10 seconds per track
- **Maximum Duration**: 4:45 (285 seconds)
- **Quality**: Excellent (with natural vocals)

### First Run / Model Download

⚠️ **Important**: On the first generation request:
1. The model will download from Hugging Face (~3.2GB)
2. This typically takes 5-15 minutes depending on internet speed
3. Ensure you have **15GB+ free disk space**
4. The app will be responsive during download (no blocking)

**Model files are cached in:** `./python/models/cache/`

### Hugging Face Authentication

Most models download automatically without authentication. If you encounter download issues:

```bash
# Login to Hugging Face
huggingface-cli login
# Enter your token when prompted (get from https://huggingface.co/settings/tokens)
```

Or set the token via environment variable:
```bash
export HF_TOKEN=your_hugging_face_token_here
```

### GPU Acceleration

**Enable GPU (NVIDIA):**
```bash
# Edit .env
CUDA_VISIBLE_DEVICES=0
```

**Enable GPU (Apple Silicon):**
PyTorch automatically uses MPS when available. No configuration needed.

**CPU-only Mode:**
```bash
# Edit .env
CUDA_VISIBLE_DEVICES=""
```

---

## 📁 Directory Structure After Setup

```
musicgen/
├── venv/                           # Python virtual environment
├── node_modules/                   # Frontend dependencies
├── backend/node_modules/           # Backend dependencies
├── output/                         # Generated audio files (.gitkeep initially)
├── python/
│   ├── models/
│   │   └── cache/                 # AI model cache (empty initially)
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── api/
│   │   │   └── generation.py     # Generation endpoints
│   │   └── services/
│   │       └── diffrhythm.py     # AI generation service
│   └── requirements.txt            # Python dependencies
├── backend/                        # Node.js backend
│   └── src/
│       ├── index.ts              # Express entry point
│       └── ...
├── storage/
│   └── database.sqlite           # SQLite database
├── .env                          # Environment configuration (created from .env.example)
└── README.md
```

---

## 🧪 Running Tests

### Frontend Tests
```bash
npm run test:frontend
```

### Backend Tests
```bash
npm run test:backend
```

### End-to-End Tests
```bash
npm run test:e2e
```

### All Tests
```bash
npm run test:all
```

---

## 📊 Environment Variables Reference

Create `.env` file with these variables (copy from `.env.example`):

### Required
```env
PORT=3001                                    # Backend port
PY_DIFFRHYTHM_URL=http://localhost:8000     # Python service URL
```

### AI Configuration
```env
MODEL_CACHE_DIR=./python/models/cache        # Where to cache AI models
CUDA_VISIBLE_DEVICES=0                       # GPU device index (or "" for CPU)
```

### Storage
```env
OUTPUT_DIR=./output                          # Generated audio files directory
TEMP_DIR=./temp                              # Temporary files
STORAGE_DIR=./storage                        # Database and cache directory
DATABASE_PATH=./storage/database.sqlite      # SQLite database location
```

### Performance
```env
MAX_CONCURRENT_JOBS=1                        # Concurrent generation jobs (1-3 recommended)
JOB_TIMEOUT=600                              # Job timeout in seconds
```

### External APIs (Optional)
```env
GEMINI_API_KEY=your_key                      # Google Gemini API
YOUTUBE_CLIENT_ID=your_id                    # YouTube API
YOUTUBE_CLIENT_SECRET=your_secret            # YouTube API
FRESHTUNES_API_KEY=your_key                  # FreshTunes API
```

---

## 🐛 Troubleshooting

### Python Service Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Verify virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r python/requirements.txt
```

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port (edit .env)
PORT=3002
```

### Frontend Won't Connect to Backend

**Error:** CORS errors in browser console

**Solution:**
1. Verify backend is running: `curl http://localhost:3001/api/health`
2. Check `.env`: `PY_DIFFRHYTHM_URL=http://localhost:8000`
3. Restart services

### Model Download Fails

**Error:** `ConnectionError` or `timeout`

**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Clear cache and retry
rm -rf python/models/cache/*

# Try with authentication
huggingface-cli login
```

### Out of Memory

**Error:** `RuntimeError: CUDA out of memory` or `MemoryError`

**Solution:**
```bash
# Switch to CPU mode (edit .env)
CUDA_VISIBLE_DEVICES=""

# Or reduce concurrent jobs
MAX_CONCURRENT_JOBS=1
```

### Database Errors

**Error:** `sqlite3.OperationalError`

**Solution:**
```bash
# Delete old database
rm storage/database.sqlite

# It will be recreated on next service start
./start-dev.sh
```

---

## 🚀 Running in Production

For production deployment, see: [DEPLOYMENT.md](../DEPLOYMENT.md)

---

## 📚 Additional Resources

- **Full Documentation**: [README.md](../README.md)
- **Architecture**: [IMPLEMENTATION.md](../IMPLEMENTATION.md)
- **Deployment**: [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Testing Guide**: [E2E-TESTING.md](./E2E-TESTING.md)
- **CI/CD Setup**: [CI-CD.md](./CI-CD.md)

---

## ✨ What's Next?

After setup is complete:

1. **Generate Music**: Open http://localhost:3000 and try generating music
2. **Explore APIs**: Check `/output` for generated files
3. **Configure Settings**: Customize `.env` for your needs
4. **Run Tests**: Verify everything works: `npm run test:all`
5. **Deploy**: Follow [DEPLOYMENT.md](../DEPLOYMENT.md) for production

---

**🎵 Ready to create music! Enjoy your local AI music generation MVP.**
