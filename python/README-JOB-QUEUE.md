# Job Queue Service

A background job management module providing queued/processing/completed/failed states, progress tracking, and optional Redis integration, persisted in SQLite.

## Features

- **Persistent Storage**: SQLite database for job persistence
- **Job States**: Comprehensive job state management (queued, processing, completed, failed, plus intermediate states)
- **Progress Tracking**: Real-time progress updates with custom messages
- **Priority Queue**: Jobs support priority-based processing
- **Redis Ready**: Designed with hooks for future Redis integration
- **FastAPI Integration**: Seamless dependency injection and BackgroundTasks support
- **RESTful API**: Complete REST API for job management
- **Type Safety**: Full TypeScript-style type safety with Pydantic models

## Architecture

```
python/app/
├── api/                    # API endpoints
│   ├── jobs.py            # Job management endpoints
│   └── generation.py      # Example generation endpoints
├── core/
│   └── database.py        # Database configuration
├── models/
│   └── job.py            # Job model and enums
├── services/
│   └── job_queue.py       # Core job queue service
├── workers/
│   └── example_worker.py  # Example worker implementation
├── dependencies.py        # FastAPI dependencies
└── main.py               # Main FastAPI application
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Service

```bash
python -m app.main
```

The service will start on `http://localhost:8000`

### 3. Create a Job

```bash
curl -X POST "http://localhost:8000/api/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "test",
    "request_data": {"prompt": "test prompt", "duration": 30},
    "priority": 5
  }'
```

### 4. Check Job Status

```bash
curl "http://localhost:8000/api/jobs/{job_id}"
```

## API Endpoints

### Job Management

- `POST /api/jobs/` - Create new job
- `GET /api/jobs/{job_id}` - Get job details
- `PUT /api/jobs/{job_id}` - Update job
- `POST /api/jobs/{job_id}/progress` - Update job progress
- `GET /api/jobs/` - List jobs (with filtering and pagination)
- `DELETE /api/jobs/{job_id}` - Delete completed/failed job
- `GET /api/jobs/stats` - Get overall job statistics
- `GET /api/jobs/stats/{job_type}` - Get job statistics by type

### Generation (Example)

- `POST /api/generate/{model}` - Start generation with specific model
- `POST /api/generate` - Start generation with default model

### System

- `GET /` - Service info
- `GET /health` - Health check

## Job States

```python
class JobStatus(str, Enum):
    QUEUED = "queued"           # Job is queued for processing
    PROCESSING = "processing"   # Job is being processed
    COMPLETED = "completed"     # Job completed successfully
    FAILED = "failed"          # Job failed
    
    # Extended statuses for specific generators
    PENDING = "pending"
    LOADING_MODEL = "loading_model"
    PREPARING_PROMPT = "preparing_prompt"
    GENERATING_AUDIO = "generating_audio"
    EXPORTING = "exporting"
    ANALYZING = "analyzing"
    RENDERING = "rendering"
```

## Usage Examples

### Using in FastAPI with BackgroundTasks

```python
from fastapi import FastAPI, BackgroundTasks, Depends
from app.services.job_queue import JobQueueService
from app.dependencies import get_job_queue_service
from app.models.job import JobStatus

app = FastAPI()

async def process_job(job_id: str, queue_service: JobQueueService):
    # Update status to processing
    queue_service.update_job(job_id, status=JobStatus.PROCESSING)
    
    # Simulate work with progress updates
    for progress in range(0, 101, 25):
        queue_service.update_progress(job_id, progress, f"Working... {progress}%")
        await asyncio.sleep(1)
    
    # Complete job
    queue_service.update_job(
        job_id,
        status=JobStatus.COMPLETED,
        result_data={"output": "result.txt"}
    )

@app.post("/start-job")
async def start_job(
    background_tasks: BackgroundTasks,
    queue_service: JobQueueService = Depends(get_job_queue_service)
):
    # Create job
    job_id = queue_service.enqueue_job(
        job_type="example",
        request_data={"input": "data"}
    )
    
    # Start background processing
    background_tasks.add_task(process_job, job_id, queue_service)
    
    return {"job_id": job_id, "status": "queued"}
```

### Creating a Worker

```python
from app.services.job_queue import JobQueueService
from app.models.job import JobStatus

class MyWorker:
    def __init__(self, worker_id: str, queue_service: JobQueueService):
        self.worker_id = worker_id
        self.queue_service = queue_service
    
    async def run(self):
        while True:
            # Get next available job
            job = self.queue_service.get_next_job(
                job_types=["my_job_type"],
                worker_id=self.worker_id
            )
            
            if job:
                await self.process_job(job)
            else:
                await asyncio.sleep(5)
    
    async def process_job(self, job):
        try:
            # Process job with progress updates
            # ... your processing logic ...
            
            # Mark as completed
            self.queue_service.update_job(
                job.id,
                status=JobStatus.COMPLETED,
                result_data={"result": "success"}
            )
        except Exception as e:
            # Mark as failed
            self.queue_service.update_job(
                job.id,
                status=JobStatus.FAILED,
                error=str(e)
            )
```

## Database Schema

The service uses SQLite with the following schema:

```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,
    status VARCHAR NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    job_type VARCHAR NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    request_data JSON,
    result_data JSON,
    message TEXT,
    error TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    worker_id VARCHAR
);
```

## Redis Integration (Future)

The service is designed with Redis integration hooks for future scaling:

```python
# Enable Redis integration
queue_service = JobQueueService(redis_enabled=True)

# Redis will be used for:
# - Job queuing and distribution
# - Real-time status updates
# - Worker coordination
# - Job result caching
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest python/tests/ -v

# Run specific test files
pytest python/tests/test_job_queue.py -v
pytest python/tests/test_job_api.py -v

# Run with coverage
pytest python/tests/ --cov=app --cov-report=html
```

## Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///./jobs.db`)
- `REDIS_URL`: Redis connection URL (optional, for future Redis integration)
- `DEBUG`: Enable debug logging (default: `false`)

## Performance Considerations

- SQLite is suitable for MVP and moderate workloads
- For high-throughput production, consider:
  - PostgreSQL for database
  - Redis for job queuing
  - Multiple worker processes
  - Connection pooling

## Monitoring

### Health Check

```bash
curl "http://localhost:8000/health"
```

### Job Statistics

```bash
curl "http://localhost:8000/api/jobs/stats"
```

### Active Jobs

```bash
curl "http://localhost:8000/api/jobs/?status=processing"
```

## Error Handling

The service provides comprehensive error handling:

- Database connection errors
- Invalid job states
- Validation errors
- Worker failures
- Timeouts

All errors are logged and propagated through the API with appropriate HTTP status codes.