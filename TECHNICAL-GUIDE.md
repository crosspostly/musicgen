# Technical Implementation Guide - MusicGen Local

## 🔧 Critical Technical Details & Solutions

This guide addresses all production-ready technical concerns including model integration, service communication, deployment, error handling, and testing.

### 1. DiffRhythm Model Integration

#### Model Download & Caching
```python
# ai-engines/diffrhythm/model_manager.py
import os
from pathlib import Path
from huggingface_hub import snapshot_download
import torch

class DiffRhythmModelManager:
    def __init__(self):
        self.cache_dir = Path(os.getenv('MODEL_CACHE_DIR', './models/cache'))
        self.model_name = "ASLP-lab/DiffRhythm-full"
        self.model = None
        self.device = self._detect_device()
        
    def _detect_device(self):
        """Automatically detect GPU/CPU"""
        if torch.cuda.is_available():
            return torch.device('cuda')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return torch.device('mps')  # Apple Silicon
        else:
            return torch.device('cpu')
    
    def download_model(self, force=False):
        """
        Download DiffRhythm model from HuggingFace
        Model size: ~3.2GB
        Cache location: ./models/cache/ASLP-lab/DiffRhythm-full
        """
        if self.is_model_cached() and not force:
            print(f"✓ Model already cached at {self.cache_dir}")
            return self.cache_dir / self.model_name
        
        print(f"Downloading DiffRhythm model ({self.model_name})...")
        print(f"Size: ~3.2GB - This may take 5-15 minutes")
        
        try:
            model_path = snapshot_download(
                repo_id=self.model_name,
                cache_dir=self.cache_dir,
                resume_download=True,  # Resume if interrupted
                local_files_only=False
            )
            print(f"✓ Model downloaded to {model_path}")
            return model_path
        except Exception as e:
            raise RuntimeError(f"Failed to download model: {e}")
    
    def load_model(self):
        """Load model into memory (requires 4-6GB RAM)"""
        if self.model is not None:
            return self.model
        
        model_path = self.download_model()
        
        print(f"Loading DiffRhythm on {self.device}...")
        from diffrhythm import DiffRhythm
        
        self.model = DiffRhythm.from_pretrained(
            model_path,
            device=self.device,
            torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32
        )
        
        print(f"✓ Model loaded on {self.device}")
        return self.model
```

#### System Requirements
```python
# installer/system_check.py
class SystemRequirements:
    REQUIREMENTS = {
        'python': '3.8+',
        'nodejs': '16+',
        'disk_space': '10GB',
        'ram': '8GB (16GB recommended with GPU)',
        'ffmpeg': 'Any version',
        'cuda': 'Optional (11.0+ for GPU acceleration)'
    }
    
    @staticmethod
    def check_cuda():
        cuda_available = torch.cuda.is_available()
        return {
            'available': cuda_available,
            'version': torch.version.cuda if cuda_available else None,
            'note': 'CPU mode: ~30-60 sec/track, GPU mode: ~10 sec/track'
        }
```

### 2. Python ↔ Node.js Communication

#### Architecture Overview
```
┌─────────────────┐         HTTP          ┌──────────────────┐
│   Node.js API   │ ◄──────────────────► │  FastAPI Python  │
│  (Port 3000)    │                       │   (Port 8000)    │
└─────────────────┘                       └──────────────────┘
        │                                          │
        │                                          │
        ▼                                          ▼
  ┌──────────┐                              ┌──────────┐
  │  Redis   │                              │  Models  │
  │ (Queue)  │                              │  Cache   │
  └──────────┘                              └──────────┘
```

#### FastAPI Service
```python
# ai-engines/diffrhythm/api.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="DiffRhythm AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}  # In-memory job storage (use Redis for production)

@app.post("/generate")
async def generate_music(request: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'pending', 'progress': 0.0}
    
    background_tasks.add_task(process_generation, job_id, request)
    
    return {'job_id': job_id, 'status': 'pending'}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {'error': 'Job not found'})

@app.get("/health")
async def health():
    return {
        'status': 'healthy',
        'model_loaded': MODEL_MANAGER.model is not None,
        'device': str(MODEL_MANAGER.device)
    }
```

#### Node.js Service Manager
```javascript
// services/ai-service-manager.js
class AIServiceManager {
    constructor() {
        this.pythonProcess = null;
        this.serviceUrl = 'http://localhost:8000';
    }
    
    async start() {
        // Check if already running
        if (await this.isHealthy()) {
            return;
        }
        
        // Start Python service
        this.pythonProcess = spawn('python', [
            '-m', 'uvicorn',
            'ai-engines.diffrhythm.api:app',
            '--host', '0.0.0.0',
            '--port', '8000'
        ]);
        
        // Auto-restart on crash
        this.pythonProcess.on('exit', (code) => {
            if (code !== 0) {
                console.log('Restarting AI service...');
                setTimeout(() => this.start(), 5000);
            }
        });
        
        await this.waitForHealthy();
    }
    
    async waitForHealthy() {
        for (let i = 0; i < 30; i++) {
            if (await this.isHealthy()) return;
            await new Promise(r => setTimeout(r, 1000));
        }
        throw new Error('AI service failed to start');
    }
}
```

### 3. Docker Deployment

#### docker-compose.yml
```yaml
version: '3.8'

services:
  ai-service:
    build:
      context: .
      dockerfile: Dockerfile.python
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./output:/app/output
    environment:
      - MODEL_CACHE_DIR=/app/models/cache
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
  
  web-service:
    build:
      context: .
      dockerfile: Dockerfile.node
    ports:
      - "3000:3000"
    depends_on:
      - ai-service
    environment:
      - AI_SERVICE_URL=http://ai-service:8000
```

#### Local Setup (без Docker)
```bash
# 1. Install Python dependencies
cd ai-engines
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 2. Install Node dependencies
cd ../web-ui
npm install

# 3. Start services
npm run start:all  # Запускает оба сервиса
```

#### package.json scripts
```json
{
  "scripts": {
    "start:ai": "cd ai-engines && python -m uvicorn diffrhythm.api:app",
    "start:web": "node server.js",
    "start:all": "concurrently \"npm run start:ai\" \"npm run start:web\"",
    "dev": "concurrently \"npm run start:ai\" \"nodemon server.js\""
  }
}
```

### 4. Job Recovery & Long Operations

#### Client-Side Persistence
```typescript
// web-ui/services/job-manager.ts
class JobManager {
    private storageKey = 'musicgen_jobs';
    
    saveJob(job: Job) {
        const jobs = this.getAllJobs();
        jobs[job.id] = job;
        localStorage.setItem(this.storageKey, JSON.stringify(jobs));
    }
    
    async resumeJobs() {
        const jobs = Object.values(this.getAllJobs());
        const activeJobs = jobs.filter(
            j => j.status === 'pending' || j.status === 'processing'
        );
        
        for (const job of activeJobs) {
            await this.pollJobStatus(job.id);
        }
    }
    
    async pollJobStatus(jobId: string) {
        const poll = async () => {
            const status = await fetch(`/api/status/${jobId}`).then(r => r.json());
            this.saveJob({ ...status, id: jobId });
            
            if (status.status === 'completed' || status.status === 'failed') {
                return status;
            }
            
            setTimeout(poll, 1000);
        };
        
        return poll();
    }
}

// Auto-resume on page load
window.addEventListener('load', () => {
    jobManager.resumeJobs();
});
```

#### Server-Side Job Queue (Redis)
```python
# Using Redis for persistent job queue
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def save_job(job_id: str, job_data: dict):
    redis_client.setex(
        f"job:{job_id}",
        3600,  # Expire after 1 hour
        json.dumps(job_data)
    )

def get_job(job_id: str):
    data = redis_client.get(f"job:{job_id}")
    return json.loads(data) if data else None
```

### 5. Error Handling

#### DiffRhythm Error Types
```python
# ai-engines/diffrhythm/errors.py
class DiffRhythmError(Exception):
    pass

class ModelNotLoadedError(DiffRhythmError):
    code = 'MODEL_NOT_LOADED'
    recovery = 'Restart AI service'

class OutOfMemoryError(DiffRhythmError):
    code = 'OUT_OF_MEMORY'
    recovery = 'Try shorter duration or CPU mode'

class InvalidPromptError(DiffRhythmError):
    code = 'INVALID_PROMPT'
    recovery = 'Simplify prompt'

ERROR_RESPONSES = {
    'MODEL_NOT_LOADED': {
        'message': 'AI model not ready',
        'recovery': 'Wait for model to load',
        'status_code': 503
    },
    'OUT_OF_MEMORY': {
        'message': 'Not enough memory',
        'recovery': 'Try shorter track',
        'status_code': 507
    }
}
```

#### Frontend Error Display
```typescript
// web-ui/components/ErrorDisplay.tsx
export function ErrorDisplay({ error }) {
    return (
        <div className="error-alert">
            <h3>⚠️ {error.message}</h3>
            {error.recovery && (
                <div className="recovery">
                    <strong>Solution:</strong> {error.recovery}
                </div>
            )}
            <button onClick={() => window.location.reload()}>
                Try Again
            </button>
        </div>
    );
}
```

### 6. Testing Strategy

#### Mock Model (без скачивания 3.2GB)
```python
# tests/mocks/diffrhythm_mock.py
import numpy as np

class MockDiffRhythm:
    def __init__(self):
        self.device = 'cpu'
    
    @staticmethod
    def from_pretrained(*args, **kwargs):
        return MockDiffRhythm()
    
    def generate(self, prompt: str, duration: int = 180):
        # Generate white noise
        audio = np.random.randn(44100 * duration) * 0.1
        return {
            'audio': audio,
            'sample_rate': 44100
        }
```

#### Integration Tests
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(monkeypatch):
    # Replace real model with mock
    monkeypatch.setattr('model_manager.DiffRhythm', MockDiffRhythm)
    from api import app
    return TestClient(app)

def test_generate(client):
    response = client.post("/generate", json={
        "prompt": "lofi beats",
        "duration": 30
    })
    
    assert response.status_code == 200
    job_id = response.json()['job_id']
    
    # Wait for completion
    for _ in range(10):
        status = client.get(f"/status/{job_id}").json()
        if status['status'] == 'completed':
            assert status['result_path'] is not None
            break
        time.sleep(1)
```

#### CI/CD with GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests with mocks
      run: pytest tests/ --cov=ai-engines
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### 7. Production Checklist

- [ ] **Model Caching**: DiffRhythm cached in `./models/cache/`
- [ ] **GPU Detection**: Auto-detect CUDA/MPS/CPU
- [ ] **Service Health**: `/health` endpoint returns 200
- [ ] **Job Persistence**: Redis or localStorage for recovery
- [ ] **Error Handling**: All errors mapped to user-friendly messages
- [ ] **Auto-restart**: Python service restarts on crash
- [ ] **Testing**: All tests pass with mocks
- [ ] **Docker**: `docker-compose up` works
- [ ] **Monitoring**: Logs accessible via `docker-compose logs`

### 8. Troubleshooting

#### "Model download fails"
```bash
# Manual download
huggingface-cli download ASLP-lab/DiffRhythm-full --local-dir ./models/cache
```

#### "Out of memory"
```bash
# Reduce batch size or use CPU
export CUDA_VISIBLE_DEVICES=""  # Force CPU mode
```

#### "Python service won't start"
```bash
# Check logs
docker-compose logs ai-service

# Restart service
docker-compose restart ai-service
```

---

*Complete technical implementation guide for production deployment.*