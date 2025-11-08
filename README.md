# MusicGen Local - AI Music Creation Suite

> 🎵 **Create, process, and monetize music with AI**  
> Local application for mass music creation and automatic distribution to streaming platforms

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org/)

## 🚀 Quick Start

For complete installation instructions, see **[INSTALL.md](INSTALL.md)**.

```bash
# Quick setup with Docker (recommended)
git clone https://github.com/crosspostly/musicgen
cd musicgen
docker-compose up

# Or use the development script
./start-dev.sh
```

**Access URLs:**
- http://localhost:3000 - Web UI
- http://localhost:3001 - Backend API  
- http://localhost:8000 - Python AI Service

**📖 Detailed Installation**: [INSTALL.md](INSTALL.md) - Complete setup guide with troubleshooting

## ✨ Core Features

- **⚡ DiffRhythm Integration** - Generate music in ~10 seconds with natural vocals
- **🎵 Audio Loop Creator** - Create 1-10 hour loops for YouTube streams  
- **📝 Metadata Editor** - Batch edit titles, artists, genres
- **🖥️ Web Interface** - Intuitive UI for all functions
- **💾 Local Processing** - No internet needed after setup

## 🎯 AI Models

| Model | Speed | Quality | Max Duration | Size |
|--------|----------|----------|--------------|--------|
| **DiffRhythm ⭐** | ~10 sec | Excellent | 4:45 min | 3.2GB |

## 📁 Project Structure

```
musicgen/
├── components/              # Reusable UI components
├── screens/                # Main application screens  
├── services/               # Frontend API integration layer
├── backend/                # Node.js + Express API server
│   ├── src/
│   │   ├── config/        # Environment and logging config
│   │   ├── controllers/   # Request handlers
│   │   ├── routes/        # API route definitions
│   │   ├── services/      # Business logic layer
│   │   ├── db/           # Database operations
│   │   ├── middleware/    # Express middleware
│   │   └── types/        # TypeScript definitions
│   ├── tests/            # Backend test suite
│   └── package.json      # Backend dependencies
├── python/                # Python FastAPI backend
│   ├── main.py           # FastAPI app entry point
│   ├── api/              # API endpoints
│   ├── services/         # AI engines and business logic
│   ├── models/           # Database models
│   └── utils/            # Utilities
├── docker-compose.yml     # Multi-service deployment
├── requirements.txt       # Python dependencies
└── .env.example          # Environment configuration
```

## Architecture

```
React SPA (Vite) ↔ Python FastAPI ↔ DiffRhythm AI
    (port 3000)      (port 8000)      (3.2GB model)
                      ↓
                  Redis Queue
                  (port 6379)
```

## 🛠️ Development

### Development Setup

📖 **For complete development setup instructions, see [INSTALL.md](INSTALL.md)**

**Quick Development Commands:**
```bash
# Install all dependencies
npm run install:all

# Start all services
./start-dev.sh

# Or start individually
npm run dev:frontend  # React dev server (port 3000)
npm run dev:backend   # Node.js backend (port 3001)
cd python && python services/diffrhythm_service.py  # Python AI service (port 8000)
```

### Available Scripts
- `npm run dev` - Start both frontend and backend concurrently
- `npm run dev:frontend` - Start React development server (port 3000)
- `npm run dev:backend` - Start Express API server (port 3001)
- `npm run build` - Build both frontend and backend
- `npm run test` - Run all tests
- `npm run test:backend` - Run backend tests only

### 📤 Export & Looping Workflow

Enhanced export screen with loop creation integration:

```javascript
// Step 1: View and download original track
// - High-quality MP3/WAV formats
// - Built-in audio player for preview
// - Metadata editing (artist, album, genre)

// Step 2: Create seamless loop
const loopOptions = {
  trackId: 'track-123',
  duration: 3600,        // 1 hour (1 min - 10 hours)
  fadeInOut: true,       // Smooth transitions
  format: 'mp3'          // or 'wav'
};

// Step 3: Track progress
// - Audio analysis for optimal loop points
// - Rendering with smooth transitions
// - Export to selected format
// - File download to local storage

// Step 4: Manage exports
// - List of all created loop files
// - Information about saved paths
// - Download buttons for ready files
```

**Features:**
- Step-by-step workflow from generation to export
- Progress bars for tracking loop creation
- Error handling with retry buttons
- File storage in local filesystem
- MP3 and WAV format support
- Configurable fade-in/out parameters

### 📺 YouTube Integration

Complete YouTube workflow automation:

```javascript
// Auto-upload with metadata
await youtube.uploadTrack({
  audioFile: 'looped_track.mp3',
  title: 'Lo-Fi Hip Hop Radio - 24/7 Study Music',
  description: 'Relaxing beats for study and work...',
  thumbnail: 'cover_1280x720.jpg',
  scheduledFor: '2025-11-07T10:00:00Z'
});
```

**Integrations:**
- YouTube Data API v3 + Upload API
- OAuth 2.0 authentication
- Content scheduler
- Automatic tags and descriptions

### 🖼️ Cover Auto Cropper

Smart cover cropping for all platforms:

```javascript
// Auto-crop to formats
await coverCropper.processImage({
  input: 'original_cover.jpg',
  formats: {
    spotify: '1000x1000',        // Square
    youtube: '1280x720',         // YouTube thumbnail
    instagram: '1080x1080'       // Instagram post
  },
  smartCrop: true  // Object/face detection
});
```

## 🧪 Testing

```bash
# Backend tests (Python)
pytest python/tests/ --cov=python

# Frontend tests (Node.js test runner)
npm test
```

## 📖 Documentation

- **[INSTALL.md](INSTALL.md)** - Complete installation and setup guide ⭐
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical architecture and setup
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## 🔒 Security

- API keys in environment variables only
- File upload size limits (max 100MB)
- Input validation with Pydantic
- Rate limiting on generation endpoints
- CORS configured for frontend access

## 🤝 Contributing

We welcome community contributions! See the implementation guide for technical details.

### Development Workflow
1. Create feature branch from main
2. Implement backend endpoints first
3. Add corresponding frontend UI
4. Write tests for both layers
5. Update documentation
6. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⭐ Star the repo if you find it useful!**

Created with ❤️ for music enthusiasts and entrepreneurs