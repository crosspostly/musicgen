# MeloGen AI v2.0 - Real AI Music Generation

> 🎵 **Create music with real MusicGen and Bark models**  
> Complete rewrite with fake models removed, full parameter support, and production-ready features

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org/)
[![Version 2.0](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/your-repo/melogen-ai)

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

### Generate Music with MusicGen

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "lo-fi hip hop with piano and rain sounds",
    "duration": 30,
    "guidance_scale": 3.0,
    "temperature": 1.0,
    "top_k": 250,
    "top_p": 0.9
  }'
```

**Response:**
```json
{
  "track_id": "123e4567-e89b-12d3-a456-426614174000",
  "audio_url": "/output/123e4567-e89b-12d3-a456-426614174000.wav",
  "duration": 30,
  "device": "cpu",
  "created_at": "2025-11-09T12:00:00Z"
}
```

### Generate Speech with Bark

```bash
curl -X POST "http://localhost:8000/api/bark" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Привет, это тест русской речи!",
    "voice_preset": "v2/ru_speaker_0",
    "language": "ru",
    "text_temp": 0.7,
    "waveform_temp": 0.7
  }'
```

### Get Track Info

```bash
curl "http://localhost:8000/api/track/123e4567-e89b-12d3-a456-426614174000"
```

## 🎯 Available Models

### MusicGen (Meta) - Instrumental Music
| Feature | Description |
|---------|-------------|
| **Model** | facebook/musicgen-small |
| **Size** | 300MB |
| **Quality** | Excellent instrumental music |
| **Speed** | ~20 seconds for 30s audio on CPU |
| **Parameters** | guidance_scale, temperature, top_k, top_p |
| **Languages** | English prompts recommended |
| **Output** | Instrumental only (no vocals) |

### Bark (Suno AI) - Speech & Vocals  
| Feature | Description |
|---------|-------------|
| **Model** | suno/bark |
| **Size** | 1.2GB |
| **Quality** | Natural speech and singing |
| **Speed** | ~30 seconds per segment |
| **Languages** | 100+ voices, Russian support |
| **Special** | Laughter, whispering, emotions |
| **Output** | Speech, singing, sound effects |

### Model Comparison
- **MusicGen**: Best for background music, beats, ambient sounds
- **Bark**: Best for voice-overs, narration, vocal effects

## ✨ Features v2.0

- **🎵 Real Models** - MusicGen (Meta) + Bark (Suno AI) - no more fakes
- **🔧 Full Parameters** - guidance_scale, temperature, top_k, top_p for MusicGen
- **🌍 Russian Support** - Bark supports Russian voices and text
- **⚡ Optimized Performance** - Real generation times, accurate estimates
- **🎛️ Professional UI** - Parameter sliders, real-time validation
- **💾 Local Processing** - No internet required after model download
- **🔧 Simple Setup** - Minimal dependencies, easy installation
- **📱 Responsive Design** - Works on desktop and mobile

## 🏗️ Architecture

```
React Frontend (3000) → FastAPI Backend (8000) → MusicGen/Bark (Transformers)
                                        ↓
                                   SQLite Database
```

### v2.0 Changes
- ✅ Replaced fake models with real MusicGen and Bark
- ✅ Added full parameter support for MusicGen
- ✅ Implemented Russian voice presets for Bark
- ✅ Updated UI with professional parameter controls
- ✅ Removed all legacy fake model code

## 📁 Project Structure

```
melogen-ai/
├── python/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── api/              # API endpoints (generation, health)
│   │   ├── services/         # MusicGen/Bark services
│   │   └── database/         # Database models
│   ├── requirements.txt      # Python dependencies
│   └── venv/                # Virtual environment
├── components/               # React components (shared)
├── screens/                 # React screens (MusicGen, Bark)
├── services/               # Frontend API layer
├── types.ts               # TypeScript interfaces
├── package.json            # Node.js dependencies
├── CHANGELOG.md           # Version history
└── README.md              # This file
```

### v2.0 Structure Changes
- `MusicGenGeneratorScreen.tsx` - Replaced DiffRhythm
- `BarkGeneratorScreen.tsx` - Enhanced with Russian voices
- Removed: `YueGeneratorScreen.tsx`, `LyriaGeneratorScreen.tsx`, `MagnetGeneratorScreen.tsx`
- New: `MusicGenParams`, `BarkParams` interfaces
- Updated: `GenerationModel`, `Screen` enums

## 🛠️ Configuration

### Environment Variables

```bash
# Model configuration
DEVICE=cpu               # cpu or cuda (auto-detected)

# Server configuration  
PORT=8000                # FastAPI port
OUTPUT_DIR=./output       # Audio file storage
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Model Information

**MusicGen**: Automatically uses `facebook/musicgen-small` (300MB)
- No configuration needed - model is fixed for v2.0
- Parameters are controlled via UI sliders

**Bark**: Uses `suno/bark` (1.2GB) when available
- Russian voice presets built-in (v2/ru_speaker_0-7)
- Full parameter support via UI controls

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