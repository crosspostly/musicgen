# MusicGen Local - AI Music Creation Suite

> 🎵 **Create music with transformers-based MusicGen**  
> Local application using only transformers library - no audiocraft, ffmpeg, or av required

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org/)

## 🚀 Quick Start

### Backend (Python FastAPI)

```bash
# Setup Python environment
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend URL:** http://localhost:8000

### Frontend (React)

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend URL:** http://localhost:3000

## 📝 API Usage

### Generate Music

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A relaxing lo-fi beat for studying",
    "duration": 30
  }'
```

**Response:**
```json
{
  "track_id": "123e4567-e89b-12d3-a456-426614174000",
  "audio_url": "/output/123e4567-e89b-12d3-a456-426614174000.mp3",
  "duration": 30,
  "device": "cpu",
  "created_at": "2025-11-09T12:00:00Z"
}
```

### Get Track Info

```bash
curl "http://localhost:8000/api/track/123e4567-e89b-12d3-a456-426614174000"
```

## 🎯 Available Models

| Model | Size | Quality | Speed | Download Size |
|-------|------|---------|-------|---------------|
| **small** | 300MB | Good | Fast | ~300MB |
| **medium** | 1.5GB | Better | Medium | ~1.5GB |
| **large** | 3GB | Best | Slow | ~3GB |

**Default:** small model (change via `MODEL_SIZE` environment variable)

## ✨ Features

- **🔥 Transformers Only** - Uses only transformers library, no audiocraft/ffmpeg/av
- **🌍 Cross-Platform** - Works on Windows, macOS, and Linux
- **⚡ Fast Generation** - Generate music in seconds
- **🎵 Multiple Formats** - Export as WAV and MP3
- **💾 Local Processing** - No internet required after setup
- **🔧 Simple Setup** - Minimal dependencies, easy installation

## 🏗️ Architecture

```
React Frontend (3000) → FastAPI Backend (8000) → MusicGen (Transformers)
                                        ↓
                                   SQLite Database
```

## 📁 Project Structure

```
musicgen/
├── python/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── api/              # API endpoints
│   │   ├── services/         # MusicGen service
│   │   └── database/         # Database models
│   ├── requirements.txt      # Python dependencies
│   └── venv/                # Virtual environment
├── components/               # React components
├── screens/                 # React screens
├── services/               # Frontend API layer
├── package.json            # Node.js dependencies
└── README.md               # This file
```

## 🛠️ Configuration

### Environment Variables

```bash
# Model configuration
MODEL_SIZE=small          # small, medium, large
DEVICE=cpu               # cpu or cuda

# Server configuration  
PORT=8000                # FastAPI port
STORAGE_DIR=./output     # Audio file storage
```

### Model Selection

Set `MODEL_SIZE` environment variable:
- `small` - Fastest, 300MB download
- `medium` - Balanced, 1.5GB download  
- `large` - Highest quality, 3GB download

## 🧪 Testing

```bash
# Run Python tests
cd python
pytest

# Run frontend tests
npm test
```

## 🔧 Development

### Installation Requirements

**Python 3.11+** with:
- torch>=2.1.0
- transformers==4.35.0
- huggingface-hub>=0.19.4
- soundfile==0.12.1
- pydub==0.25.1

**Node.js 16+** for frontend

### Key Dependencies

**Required:**
- transformers (MusicGen model)
- torch (PyTorch backend)
- soundfile (audio saving)
- pydub (MP3 conversion)

**NOT Required:**
- ❌ audiocraft
- ❌ ffmpeg
- ❌ av
- ❌ librosa

## 🌍 Cross-Platform Support

This implementation uses only transformers and standard Python libraries, ensuring:

- **Windows** compatibility (no ffmpeg/av installation needed)
- **macOS** support (Apple Silicon and Intel)
- **Linux** compatibility (all distributions)
- **Docker** friendly (minimal system dependencies)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⭐ Star the repo if you find it useful!**

Created with ❤️ for music enthusiasts and developers