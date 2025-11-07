# MVP Task Refinement - MusicGen Local

Analysis of actual codebase state and refined 6 MVP tasks based on real implementation requirements.

## 📊 Current Codebase Analysis

### Frontend Status (~20% Complete)
**✅ Implemented:**
- React 19 + Vite + TypeScript setup
- Type definitions (`types.ts`) with GenerationModel and Screen enums
- Component library (`components/common.tsx`, `components/icons.tsx`)
- Screen routing system in `App.tsx`
- 9 placeholder screens with basic UI structure
- Google GenAI SDK integration (placeholder service)

**⚠️ Stubbed/Incomplete:**
- All API calls point to `/api/generate` (non-existent endpoint)
- No error handling UI components
- No audio player implementation
- No progress indicators for long operations
- No job status polling logic
- No real file upload/download handling

**❌ Missing Critical Pieces:**
- Audio preview/playback functionality
- Real-time job progress tracking
- Batch processing UI
- Settings/configuration panel
- System health monitoring

### Backend Status (~0% Complete)
**✅ Defined (Documentation Only):**
- Complete `requirements.txt` with all dependencies
- `docker-compose.yml` configuration
- Environment variables in `.env.example`

**❌ Completely Missing:**
- No Python service files (`backend/` directory doesn't exist)
- No FastAPI application
- No AI engine implementations
- No API endpoints
- No job queue system
- No audio processing utilities
- No Dockerfiles (referenced in docker-compose.yml)

### Infrastructure Gaps
- Dockerfiles referenced but don't exist
- No backend directory structure
- No testing framework setup
- No CI/CD configuration

---

## 🎯 Refined 6 MVP Tasks

Based on actual codebase analysis, here are the 6 focused tasks needed for MVP completion:

### Task 1: Backend Infrastructure Scaffold (3-4 hours)

**Scope**: Create complete backend foundation from scratch

**Files to Create:**
```
backend/
├── main.py                    # FastAPI app entry point
├── models/
│   └── schemas.py            # Pydantic models for API
├── api/
│   ├── __init__.py
│   ├── generate.py           # Music generation endpoints
│   └── health.py             # Health check endpoints
├── ai-engines/
│   ├── __init__.py
│   └── base_engine.py        # Abstract base class for AI engines
├── utils/
│   ├── __init__.py
│   ├── storage.py            # File management utilities
│   └── audio.py              # Audio processing helpers
└── tests/
    ├── __init__.py
    └── test_api.py           # Basic API tests
```

**Implementation Details:**
- FastAPI application with CORS support
- Basic health check endpoint (`/health`)
- Pydantic models for request/response validation
- File upload handling with temporary storage
- Error handling middleware
- Basic logging configuration

**Acceptance Criteria:**
- FastAPI server starts on port 8000
- `/health` endpoint returns 200 OK
- File upload works for audio files
- CORS configured for frontend (port 3000)
- Basic error responses with proper HTTP status codes

**Dependencies:**
- FastAPI, Uvicorn, Pydantic (already in requirements.txt)
- aiofiles for file handling

---

### Task 2: DiffRhythm AI Engine Integration (4-6 hours)

**Scope**: Implement DiffRhythm model download, caching, and generation

**Files to Modify/Create:**
```
backend/ai-engines/
├── diffrhythm/
│   ├── __init__.py
│   ├── model_manager.py     # Model download and caching
│   └── generator.py         # Music generation logic
└── base_engine.py           # Update with concrete implementation

backend/api/
└── generate.py              # Add DiffRhythm endpoint implementation
```

**Implementation Details:**
- HuggingFace model download (ASLP-lab/DiffRhythm-full, 3.2GB)
- GPU/CPU/MPS device auto-detection
- Model caching with resume capability
- Generation endpoint with prompt processing
- Error handling for model loading failures
- Generation timeout handling (10 minutes max)

**API Endpoint:**
```python
POST /api/generate
{
  "model": "DiffRhythm",
  "prompt": "Lo-fi hip hop with rain sounds",
  "duration": 180,
  "parameters": {
    "genre": "Electronic",
    "mood": "Relaxed"
  }
}
```

**Acceptance Criteria:**
- Model downloads automatically on first use
- Generation works on both GPU and CPU
- Proper error handling for missing models/timeouts
- Returns audio file URL and metadata
- Generation time: ~10s (GPU), ~30-60s (CPU)

**Frontend Integration:**
- Update `DiffRhythmGeneratorScreen.tsx` to call real API
- Add progress indicators during generation
- Handle error states properly

---

### Task 3: Job Queue & Persistence System (2-3 hours)

**Scope**: Implement Redis-based job management for long-running operations

**Files to Create:**
```
backend/
├── models/
│   └── job.py               # Job model and status enums
├── services/
│   ├── __init__.py
│   ├── job_manager.py       # Redis job queue management
│   └── storage.py           # Job persistence logic
└── api/
    ├── jobs.py              # Job status endpoints
    └── generate.py           # Update to use job queue
```

**Implementation Details:**
- Redis connection and job queue management
- Job status tracking (pending, processing, completed, failed)
- Job TTL management (1 hour)
- Client-side job polling logic
- Browser localStorage backup for job recovery

**Job Schema:**
```python
{
  "id": "uuid",
  "status": "pending|processing|completed|failed",
  "model": "DiffRhythm",
  "created_at": "2024-01-01T00:00:00Z",
  "result": {
    "audio_url": "/output/track_123.mp3",
    "duration": 180,
    "metadata": {...}
  }
}
```

**Frontend Updates:**
- Add job polling to `services/api.ts`
- Update screens to handle async job completion
- Implement localStorage backup for job recovery

**Acceptance Criteria:**
- Jobs persist through browser refresh
- Long-running operations don't timeout
- Job status updates in real-time
- Failed jobs show proper error messages
- Redis cleanup for expired jobs

---

### Task 4: Audio Loop Creator (4-5 hours)

**Scope**: Implement audio looping service for YouTube streams

**Files to Create:**
```
backend/api/
└── loop_creator.py          # Audio looping endpoints

backend/services/
└── audio_looper.py          # Loop creation logic

frontend/screens/
└── LoopCreatorScreen.tsx    # New UI for loop creation
```

**Implementation Details:**
- Audio analysis using librosa (beat detection, tempo analysis)
- Seamless loop point detection
- Fade-in/fade-out transitions
- Support for 1 minute to 10 hour durations
- Multiple output formats (MP3, WAV)

**Algorithm:**
1. Analyze audio start/end compatibility
2. Detect optimal loop points using spectral analysis
3. Apply crossfade transitions
4. Generate extended audio file
5. Optimize for streaming platforms

**API Endpoint:**
```python
POST /api/loop/create
{
  "input_file": "track.mp3",
  "target_duration": "2h",
  "fade_duration": 5,
  "output_format": "mp3"
}
```

**Frontend Integration:**
- Add loop creator to navigation
- File upload with drag-and-drop
- Duration selector with presets
- Progress bar for processing
- Preview and download functionality

**Acceptance Criteria:**
- Creates seamless loops without clicks/pops
- Supports various target durations
- Handles different audio formats
- Processing time: <30 seconds for typical tracks
- Quality preservation in extended tracks

---

### Task 5: Metadata Editor & Export System (2-3 hours)

**Scope**: Complete metadata management and file export functionality

**Files to Modify:**
```
frontend/screens/
└── MetadataEditorScreen.tsx  # Complete functionality

backend/api/
└── metadata.py               # Metadata management endpoints

frontend/screens/
└── ExportScreen.tsx          # Complete export functionality
```

**Implementation Details:**
- Backend API for metadata CRUD operations
- Audio file export with metadata embedding
- Support for multiple export formats
- Batch metadata editing capabilities
- File download with proper headers

**Metadata Schema:**
```python
{
  "track_id": "uuid",
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "genre": "Genre",
  "duration": 180,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Frontend Features:**
- Form validation for required fields
- Auto-save functionality
- Preview of metadata in audio player
- Export format selection
- Download progress indicators

**Acceptance Criteria:**
- Metadata persists in database
- Audio files include metadata in exports
- Form validation prevents invalid data
- Export works for all supported formats
- Batch processing for multiple tracks

---

### Task 6: Frontend Integration & Polish (3-4 hours)

**Scope**: Complete frontend integration with real APIs and add polish

**Files to Modify:**
```
frontend/services/
└── api.ts                   # Real API client implementation

frontend/screens/
├── DiffRhythmGeneratorScreen.tsx  # Complete integration
├── ModelSelectionScreen.tsx       # Add model descriptions
├── MetadataEditorScreen.tsx       # Complete functionality
└── ExportScreen.tsx               # Complete functionality

frontend/components/
├── common.tsx              # Add error handling, progress components
└── AudioPlayer.tsx         # New audio player component
```

**Implementation Details:**
- Real API client replacing placeholder calls
- Error handling with user-friendly messages
- Progress indicators for all async operations
- Audio player with waveform visualization
- Responsive design improvements
- Loading states for all screens

**API Integration:**
- Replace all `/api/generate` calls with real endpoints
- Add job polling for long operations
- Implement proper error handling
- Add retry logic for failed requests

**New Components:**
- `AudioPlayer` - Play/pause, seek, volume controls
- `ProgressBar` - Generation and processing progress
- `ErrorDisplay` - User-friendly error messages
- `LoadingSpinner` - Consistent loading states

**Acceptance Criteria:**
- All screens work with real backend APIs
- No more placeholder functionality
- Smooth user experience with proper feedback
- Responsive design works on mobile/desktop
- Error states handled gracefully
- Audio playback works in all modern browsers

---

## 📈 Task Dependencies & Timeline

### Dependency Graph
```
Task 1 (Backend) → Task 2 (DiffRhythm) → Task 3 (Jobs)
Task 1 (Backend) → Task 4 (Audio Looper)
Task 1 (Backend) → Task 5 (Metadata)
Task 2 + Task 3 + Task 5 → Task 6 (Frontend Integration)
```

### Estimated Timeline
- **Week 1**: Task 1 (Mon-Tue), Task 2 (Wed-Fri)
- **Week 2**: Task 3 (Mon-Tue), Task 4 (Wed-Fri)
- **Week 3**: Task 5 (Mon-Tue), Task 6 (Wed-Fri)

**Total Estimated Effort**: 18-25 hours over 3 weeks

### Risk Assessment
**High Risk**: Task 2 (DiffRhythm integration) - Model download and GPU compatibility
**Medium Risk**: Task 4 (Audio looping) - Complex audio processing
**Low Risk**: Tasks 1, 3, 5, 6 - Standard web development

---

## 🎯 MVP Success Criteria

After completing these 6 tasks:

### Functional Requirements
✅ Users can generate music using DiffRhythm AI model  
✅ Generated tracks can be extended to long loops  
✅ Metadata can be edited and embedded in exports  
✅ All operations work asynchronously with progress feedback  
✅ System handles errors gracefully with recovery options  

### Technical Requirements  
✅ Full-stack application with React + FastAPI
✅ Redis job queue for long-running operations  
✅ Docker deployment ready  
✅ Basic test coverage for critical paths  
✅ Responsive UI that works on modern browsers  

### Performance Requirements
✅ Music generation: <60 seconds (CPU), <15 seconds (GPU)  
✅ Audio looping: <30 seconds processing time  
✅ File uploads: Support up to 100MB files  
✅ Concurrent users: Support 3 simultaneous generations  

This refined task plan focuses on bridging the gap from the current 20% frontend implementation to a fully functional MVP, with realistic estimates based on the actual codebase state.