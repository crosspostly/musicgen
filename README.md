# MusicGen Local - AI Music Creation Suite

> 🎵 **Create, process, and monetize music with AI**  
> Local application for mass music creation and automatic distribution to streaming platforms

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org/)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/crosspostly/musicgen
cd musicgen

# Run with Docker (recommended)
docker-compose up

# Or run locally
npm install
pip install -r requirements.txt
npm run dev
```

Web interface opens at `http://localhost:3000`

## ✨ Core Features (MVP Phase 1)

- **⚡ DiffRhythm Integration** - Generate music in ~10 seconds with natural vocals
- **🎵 Audio Loop Creator** - Create 1-10 hour loops for YouTube streams  
- **📝 Metadata Editor** - Batch edit titles, artists, genres
- **🖥️ Web Interface** - Intuitive UI for all functions

## 🎯 AI Models

| Model | Speed | Quality | Max Duration | Size |
|--------|----------|----------|--------------|--------|
| **DiffRhythm ⭐** | ~10 sec | Excellent | 4:45 min | 3.2GB |

## 📁 Project Structure

```
musicgen/
├── frontend/                 # React 19 + Vite web app
│   ├── components/          # Reusable UI components
│   ├── screens/            # Main application screens
│   └── services/           # API integration layer
├── backend/                 # FastAPI Python service
│   ├── ai-engines/         # AI model integrations
│   └── api/                # REST API endpoints
├── docker-compose.yml      # Multi-service deployment
├── requirements.txt        # Python dependencies
└── .env.example           # Environment configuration
```

## 🛠️ Development

### System Requirements
- **Node.js** 16+ 
- **Python** 3.8+
- **Docker** (optional but recommended)
- **Free space**: 5GB+ for AI models

### Setup
```bash
# Copy environment file
cp .env.example .env

# Install dependencies
npm install
pip install -r requirements.txt

# Start development servers
npm run dev  # Frontend (port 3000)
python -m uvicorn backend.main:app --reload  # Backend (port 8000)
```

## 📖 Documentation

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical architecture and setup
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## 🤝 Contributing

We welcome community contributions! See the implementation guide for technical details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⭐ Star the repo if you find it useful!**

Created with ❤️ for music enthusiasts and entrepreneurs