# MusicGen Local

Generate AI music locally. No cloud dependencies.

## Quick Start

```bash
# Option 1: Docker (recommended)
docker-compose up

# Option 2: Local development
./install.sh && npm run dev
```

**URLs:**
- http://localhost:3000 - Web UI
- http://localhost:8000 - Python API

## Features

- 🎵 **DiffRhythm**: Generate 30sec music (~10 sec)
- 🎚️ **Audio Loop**: Create 1-10 hour loops for streams
- 🏷️ **Metadata**: Batch edit track info
- 💾 **Local**: No internet needed after setup

## Requirements

**Option A: Docker**
- Docker Desktop 20.10+
- 10GB free space

**Option B: Local Install**
- Python 3.9+ (backend runtime)
- Node.js 16+ (frontend dev only - npm/Vite)
- FFmpeg (audio processing)
- 10GB free space
- GPU optional (NVIDIA CUDA recommended)

## Architecture

```
React SPA (Vite) ↔ Python FastAPI ↔ DiffRhythm AI
    (port 3000)      (port 8000)      (3.2GB model)
```

## Documentation

- **[SETUP-GUIDE.md](SETUP-GUIDE.md)** - Detailed installation
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment

## License

MIT License
