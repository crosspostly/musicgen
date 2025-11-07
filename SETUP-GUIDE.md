# 🚀 MusicGen Local - Setup Guide

Complete installation guide for MusicGen Local MVP.

---

## 📋 What is MusicGen Local?

Local AI music generation platform:
- **Create music** with AI (DiffRhythm)
- **Process audio** (loops, metadata)
- **100% local** - no cloud dependencies

---

## ⚡ Quick Start (5 minutes)

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/crosspostly/musicgen
cd musicgen
docker-compose up
```

Open http://localhost:3000

### Option 2: Local Development

```bash
git clone https://github.com/crosspostly/musicgen
cd musicgen
cp .env.example .env

# Backend (Python)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (npm for dev only)
npm install

# Start services (3 terminals)
redis-server                                              # Terminal 1
python -m uvicorn python.main:app --reload --port 8000    # Terminal 2
npm run dev                                               # Terminal 3
```

Open http://localhost:3000

---

## 💻 System Requirements

### Minimum (Audio Processing Only)
- **OS**: Windows 10/11, macOS 12+, Ubuntu 20.04+
- **RAM**: 4GB
- **Storage**: 2GB
- **Software**: Python 3.9+, FFmpeg

### Recommended (With AI Generation)
- **OS**: Windows 10/11, macOS 12+, Ubuntu 20.04+
- **RAM**: 8GB+
- **Storage**: 10GB+
- **GPU**: NVIDIA (CUDA) or Apple Silicon (MPS)
- **Software**: Python 3.9+, FFmpeg, Redis 7+

**Note:** Node.js 16+ is only needed for frontend development (npm/Vite). The backend runs entirely on Python.

---

## 🔧 Manual Installation

### Step 1: Install Dependencies

**Windows:**
```powershell
# Install Python from https://python.org
# Install FFmpeg: winget install FFmpeg
# Install Redis: winget install Redis.Redis
```

**macOS:**
```bash
brew install python@3.9 ffmpeg redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y python3.9 python3-pip ffmpeg redis-server
```

### Step 2: Clone Repository

```bash
git clone https://github.com/crosspostly/musicgen
cd musicgen
```

### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (optional)
```

### Step 4: Install Python Packages

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Install Frontend Dev Tools (Optional)

Only needed if you want to modify the frontend:

```bash
# Node.js from https://nodejs.org
npm install
```

### Step 6: Start Services

**Terminal 1 - Redis (Job Queue):**
```bash
redis-server
```

**Terminal 2 - Python Backend:**
```bash
python -m uvicorn python.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend Dev Server (if developing):**
```bash
npm run dev
```

**Or serve pre-built frontend:**
```bash
npm run build
python -m http.server 3000 --directory dist
```

Open http://localhost:3000

---

## 🎵 AI Models

Models download automatically on first use:

### DiffRhythm ⭐ (Recommended)
- **Size**: 3.2GB
- **Speed**: ~10 sec/track (GPU), ~30-60 sec (CPU)
- **Quality**: Excellent, natural vocals
- **Duration**: Up to 4:45 minutes
- **Best for**: Streaming platforms

---

## 🔗 Redis Configuration

Redis is used for:
- Job queue for music generation
- Task state persistence
- Progress tracking

**Default configuration (local):**
```bash
# Check Redis status
redis-cli ping
# Should return: PONG

# View jobs
redis-cli keys "*"

# Clear cache (if needed)
redis-cli FLUSHALL
```

**Environment variable:**
```env
REDIS_URL=redis://localhost:6379
```

---

## 📊 Project Structure

```
musicgen/
├── python/                # Python FastAPI backend
│   ├── main.py           # FastAPI entry point
│   ├── api/              # API endpoints
│   ├── services/         # Business logic (DiffRhythm, loops)
│   └── tests/            # Backend tests
│
├── src/                  # React frontend
│   ├── App.tsx           # Main app
│   ├── screens/          # UI screens
│   ├── components/       # Reusable components
│   └── services/         # API clients
│
├── models/               # AI models cache
│   └── cache/            # HuggingFace cache
│
├── output/               # Generated files
│   ├── audio/            # Audio tracks
│   └── exports/          # Loop exports
│
├── docker-compose.yml    # Docker configuration
├── requirements.txt      # Python dependencies
└── package.json          # Frontend dev dependencies (npm/Vite)
```

---

## 🚨 Troubleshooting

### Redis Not Starting
```bash
# Check if port 6379 is in use
lsof -i :6379  # macOS/Linux
netstat -ano | findstr :6379  # Windows

# Change port in .env if needed
REDIS_PORT=6380
```

### AI Model Download Fails
```bash
# Check internet connection
ping huggingface.co

# Manual download
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ASLP-lab/DiffRhythm-full')"
```

### GPU Not Detected
```bash
# NVIDIA
nvidia-smi

# Apple Silicon
python -c "import torch; print(torch.backends.mps.is_available())"

# CPU fallback is automatic (slower)
```

### Port Already in Use
```bash
# Change ports in .env
BACKEND_PORT=8001  # instead of 8000
FRONTEND_PORT=3001 # instead of 3000
REDIS_PORT=6380    # instead of 6379
```

---

## 📖 Additional Documentation

- **[README.md](README.md)** - Quick overview
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment

---

## ⭐ Next Steps

1. **Start the application**: Use Docker or local setup
2. **Select DiffRhythm model**: Recommended for MVP
3. **Generate your first track**: Enter text prompt
4. **Create audio loops**: 1-10 hours for streaming
5. **Edit metadata**: Add artist, album, genre info

**Start creating music locally!** 🎵
