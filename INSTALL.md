# Installation Guide

Complete installation instructions for DiffRhythm AI Music Generator with three-service architecture.

## 🚀 Quick Start

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
./start-dev.sh
```
Open http://localhost:3000

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **RAM**: 8GB (16GB+ recommended for AI generation)
- **Storage**: 10GB+ free space (for AI models and generated files)
- **Python**: 3.9+
- **Node.js**: 16+
- **FFmpeg**: Required for audio processing

### Recommended (for AI Generation)
- **GPU**: NVIDIA CUDA-compatible GPU or Apple Silicon (MPS)
- **RAM**: 16GB+
- **Storage**: 20GB+ SSD (for better performance)

---

## 🔧 Manual Installation

### Step 1: Install System Dependencies

**Windows:**
```powershell
# Install Python from https://python.org
# Install Node.js from https://nodejs.org
# Install FFmpeg: winget install FFmpeg
```

**macOS:**
```bash
brew install python@3.9 node ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y python3.9 python3-pip nodejs npm ffmpeg
```

### Step 2: Clone Repository

```bash
git clone https://github.com/crosspostly/musicgen
cd musicgen
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# See Environment Variables section below
```

### Step 4: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install Python packages
pip install -r python/requirements.txt
```

### Step 5: Install Node.js Dependencies

```bash
# Install frontend and backend dependencies
npm run install:all
```

### Step 6: Initialize Database

```bash
# Create storage directory and initialize SQLite database
mkdir -p storage
# The database will be created automatically when the backend starts
```

---

## 🎯 Service Architecture

The application consists of three main services:

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| **Frontend** | 3000 | React + Vite | Web interface |
| **Backend** | 3001 | Node.js + Express | API server with SQLite |
| **Python AI Service** | 8000 | Python + FastAPI | DiffRhythm AI generation |

### Service Communication
```
React Frontend (3000) ↔ Node.js Backend (3001) ↔ Python AI Service (8000)
                                           ↓
                                      SQLite Database
```

**⚠️ Port Configuration Note**: 
- The `.env.example` file shows `PY_DIFFRHYTHM_URL=http://localhost:8001` but the Python service actually runs on port 8000
- Update your `.env` file to use `PY_DIFFRHYTHM_URL=http://localhost:8000` for proper connectivity

---

## 🚀 Starting Services

### Option 1: Development Script (Recommended)

```bash
# Start all services with automatic dependency installation
./start-dev.sh
```

This script will:
- Check and install dependencies
- Start Python AI service (port 8000)
- Start Node.js backend (port 3001)
- Start React frontend (port 3000)

### Option 2: Manual Terminal Startup

Open 3 separate terminals:

**Terminal 1 - Python AI Service:**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
python python/services/diffrhythm_service.py
```

**Terminal 2 - Node.js Backend:**
```bash
cd backend
npm run dev
```

**Terminal 3 - React Frontend:**
```bash
npm run dev
```

### Option 3: Individual Service Commands

```bash
# Frontend only
npm run dev:frontend

# Backend only
npm run dev:backend

# Python AI service only
cd python && python services/diffrhythm_service.py

# All services together
npm run dev:full
```

---

## 🔗 Health Checks

Verify all services are running:

```bash
# Frontend (should return HTML)
curl http://localhost:3000

# Backend API
curl http://localhost:3001/api/health

# Python AI Service
curl http://localhost:8000/health
```

Expected response format:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "service": "backend|python|frontend"
}
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure these variables:

### Core Configuration
```env
# Service URLs
AI_SERVICE_URL=http://localhost:8000          # Python AI service
WEB_SERVICE_URL=http://localhost:3000         # Frontend URL

# Backend Configuration
NODE_ENV=development                          # development|production
PORT=3001                                     # Node.js backend port
PY_DIFFRHYTHM_URL=http://localhost:8000       # Python service URL (note: .env.example shows 8001, but service runs on 8000)
STORAGE_DIR=./storage                         # File storage directory
DATABASE_PATH=./storage/database.sqlite       # SQLite database path
FFMPEG_PATH=ffmpeg                           # FFmpeg executable path
```

### AI Model Configuration
```env
# Model Settings
MODEL_CACHE_DIR=./models/cache                # AI model cache directory
CUDA_VISIBLE_DEVICES=0                        # GPU device ("" for CPU mode)
```

### Performance Settings
```env
# Job Processing
MAX_CONCURRENT_JOBS=3                         # Max simultaneous AI jobs
JOB_TIMEOUT=600                              # Job timeout in seconds
```

### Storage Directories
```env
# File Storage
OUTPUT_DIR=./output                          # Generated audio files
TEMP_DIR=./temp                             # Temporary files
```

### Optional API Keys
```env
# External Integrations (optional)
GEMINI_API_KEY=your_gemini_api_key_here
FRESHTUNES_API_KEY=your_freshtunes_api_key_here
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
```

---

## 📁 Directory Structure

After installation, your directory structure will look like:

```
musicgen/
├── venv/                    # Python virtual environment
├── node_modules/            # Node.js dependencies
├── storage/                 # SQLite database and files
│   ├── database.sqlite      # Main database
│   └── jobs/               # Job-related files
├── output/                  # Generated audio files
├── models/cache/            # AI model cache
├── temp/                    # Temporary files
├── backend/                 # Node.js backend source
├── python/                  # Python AI service source
├── src/                     # React frontend source
└── .env                     # Environment configuration
```

---

## 🧪 Testing Installation

### Basic Functionality Test

1. **Open Web Interface**: http://localhost:3000
2. **Generate Music**: 
   - Enter a prompt like "Relaxing lo-fi beat"
   - Click Generate
   - Wait for completion (10-60 seconds)
3. **Check Results**: Verify audio file is generated and playable

### API Test

```bash
# Test backend health
curl http://localhost:3001/api/health

# Test Python service health
curl http://localhost:8000/health

# Generate music via API
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test beat", "durationSeconds": 10}'
```

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or change port in .env
PORT=3002  # Change backend port
```

### Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r python/requirements.txt
```

### FFmpeg Not Found
```bash
# Verify FFmpeg installation
ffmpeg -version

# Install if missing
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from ffmpeg.org
```

### AI Model Download Fails
```bash
# Check internet connection
ping huggingface.co

# Clear model cache and retry
rm -rf models/cache
# Restart service to re-download
```

### GPU Not Detected
```bash
# Check NVIDIA GPU
nvidia-smi

# Check Apple Silicon
python -c "import torch; print(torch.backends.mps.is_available())"

# Force CPU mode (add to .env)
CUDA_VISIBLE_DEVICES=""
```

### Database Permission Issues
```bash
# Check storage directory permissions
ls -la storage/

# Fix permissions
chmod 755 storage/
chmod 644 storage/database.sqlite
```

### Service Won't Start
```bash
# Check logs for each service
# Backend: Look at terminal output
# Python: Look at terminal output
# Frontend: Look at browser console

# Common issues:
# - Missing dependencies: Run npm run install:all
# - Python packages: pip install -r python/requirements.txt
# - Environment variables: Verify .env file exists
```

### Memory Issues
```bash
# Reduce concurrent jobs (add to .env)
MAX_CONCURRENT_JOBS=1

# Use CPU mode (add to .env)
CUDA_VISIBLE_DEVICES=""
```

---

## 🐳 Docker Installation

For containerized deployment:

```bash
# Build and start all services
docker-compose up

# Build without starting
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Docker handles all dependencies and port mappings automatically.

---

## 📖 Next Steps

1. **Explore Features**: Try generating different music styles
2. **Configure Settings**: Adjust AI parameters and output formats
3. **Integrate APIs**: Set up external service integrations
4. **Production Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

## 🆘 Additional Help

- **Documentation**: [README.md](README.md), [SETUP-GUIDE.md](SETUP-GUIDE.md)
- **Architecture**: [IMPLEMENTATION.md](IMPLEMENTATION.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: Check GitHub Issues for common problems

---

**🎵 Ready to create music! Your local AI music generator is now installed and running.**