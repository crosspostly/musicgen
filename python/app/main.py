"""
Main FastAPI application with job queue service integration
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_db
from .api import jobs
from .services.job_queue import JobQueueService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up job queue service...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Initialize job queue service
    app.state.job_queue = JobQueueService()
    logger.info("Job queue service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down job queue service...")


# Create FastAPI app
app = FastAPI(
    title="Job Queue Service",
    description="Background job management with queued/processing/completed/failed states, progress tracking, and optional Redis integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router)
from .api import generation
app.include_router(generation.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Job Queue Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        with app.state.job_queue.get_db_session() as db:
            db.execute("SELECT 1")
        
        # Get job stats
        stats = app.state.job_queue.get_job_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "job_stats": {
                "total_jobs": stats.get("total", 0),
                "active_jobs": stats.get("active", 0)
            },
            "redis_enabled": app.state.job_queue.redis_enabled
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )