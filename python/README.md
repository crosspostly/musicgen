# DiffRhythm Python Service

FastAPI microservice for AI music generation using the DiffRhythm model.

## Features

- 🚀 **Fast Generation**: Generate music in ~10 seconds using DiffRhythm
- 🌍 **Multi-language Support**: Russian and English prompts
- 📊 **Progress Tracking**: Real-time job status and progress updates
- 🎵 **Multiple Formats**: Export to WAV (44.1kHz 16-bit) and MP3 (320kbps)
- 🔧 **GPU/CPU Support**: Automatic CUDA detection with CPU fallback
- 📈 **Async Processing**: Non-blocking job processing with background tasks

## Requirements

- Python 3.8+
- FFmpeg (for MP3 conversion)
- 5GB+ free disk space for model cache
- CUDA-compatible GPU (recommended) or CPU

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

### 3. Start Service

```bash
# Development mode
python services/diffrhythm_service.py

# Production mode
uvicorn services.diffrhythm_service:app --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

### 4. Verify Installation

```bash
curl http://localhost:8000/health
```

## API Endpoints

### Generate Music

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Relaxing lo-fi hip hop beat for studying",
    "durationSeconds": 30,
    "language": "en",
    "genre": "lo-fi",
    "mood": "relaxing"
  }'
```

**Response:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "accepted",
  "message": "Generation job started"
}
```

### Check Job Status

```bash
curl "http://localhost:8000/status/12345678-1234-1234-1234-123456789abc"
```

**Response:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "generating_audio",
  "progress": 65,
  "message": "Generating audio..."
}
```

### Get Job Result

```bash
curl "http://localhost:8000/result/12345678-1234-1234-1234-123456789abc"
```

**Response:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "completed",
  "duration": 30.0,
  "wav_file": {
    "file_path": "/app/output/12345678-1234-1234-1234-123456789abc.wav",
    "file_size": 5242880,
    "file_url": "/files/12345678-1234-1234-1234-123456789abc.wav",
    "file_name": "12345678-1234-1234-1234-123456789abc.wav"
  },
  "mp3_file": {
    "file_path": "/app/output/12345678-1234-1234-1234-123456789abc.mp3",
    "file_size": 1048576,
    "file_url": "/files/12345678-1234-1234-1234-123456789abc.mp3",
    "file_name": "12345678-1234-1234-1234-123456789abc.mp3"
  },
  "metadata": {
    "prompt": "Relaxing lo-fi hip hop beat for studying",
    "language": "en",
    "genre": "lo-fi",
    "mood": "relaxing",
    "created_at": "2024-01-01T12:00:00",
    "completed_at": "2024-01-01T12:00:10"
  }
}
```

## Job Status Flow

Jobs progress through these stages:

1. **pending** - Job created, waiting to start
2. **loading_model** - DiffRhythm model is being loaded (~2 seconds)
3. **preparing_prompt** - Processing text prompt (~1 second)
4. **generating_audio** - Generating audio (~3-7 seconds)
5. **exporting** - Converting to WAV/MP3 formats (~1 second)
6. **completed** - Job finished successfully
7. **failed** - Job failed with error

## Configuration

Environment variables:

```bash
# Storage directory for generated files
export STORAGE_DIR="./output"

# Model cache directory (default: ~/.cache/diffrhythm)
export MODEL_CACHE_DIR="/path/to/model/cache"

# CUDA device selection (default: auto-detect)
export CUDA_VISIBLE_DEVICES="0"
```

## Model Information

- **Model Size**: ~3.2GB (downloaded on first run)
- **Sample Rate**: 44.1kHz
- **Audio Quality**: 16-bit WAV, 320kbps MP3
- **Max Duration**: 300 seconds (5 minutes)
- **Languages**: English (en), Russian (ru)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=services tests/
```

### Project Structure

```
python/
├── services/
│   └── diffrhythm_service.py    # Main FastAPI service
├── tests/
│   └── test_diffrhythm.py       # Test suite
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Troubleshooting

### Common Issues

**1. CUDA not detected**
```
Warning: CUDA not available, using CPU (slower generation)
```
- Solution: Install CUDA toolkit and PyTorch with CUDA support
- CPU mode will work but be significantly slower

**2. FFmpeg not found**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```
- Solution: Install FFmpeg and ensure it's in your PATH

**3. Model download fails**
```
HTTPError: 503 Server Error: Service Unavailable
```
- Solution: Check internet connection and Hugging Face availability
- Models are cached after first download

**4. Out of memory**
```
RuntimeError: CUDA out of memory
```
- Solution: Reduce batch size or use CPU mode
- Close other GPU applications

### Performance Tips

1. **Use GPU**: CUDA generation is 5-10x faster than CPU
2. **Warm Start**: First generation loads model (~2 seconds)
3. **Batch Processing**: Process multiple jobs concurrently
4. **SSD Storage**: Use fast storage for model cache and output

## Integration with Node.js Backend

The service is designed to work with the Node.js backend:

1. Node.js submits jobs via `POST /generate`
2. Polls status via `GET /status/{job_id}`
3. Retrieves results via `GET /result/{job_id}`
4. Downloads files via `/files/{filename}`

## License

MIT License - see LICENSE file for details.