"""
FastAPI application for DiffRhythm music generation with direct prompt → track flow
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_database
from .api import generation
from .dependencies import set_diffrhythm_service
from .services.diffrhythm import DiffRhythmService

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
    logger.info("Starting up DiffRhythm service...")
    
    settings = get_settings()
    
    # Initialize database
    init_database()
    logger.info("Database initialized")
    
    # Initialize DiffRhythm service
    storage_dir = os.getenv("OUTPUT_DIR", "./output")
    os.makedirs(storage_dir, exist_ok=True)
    
    service = DiffRhythmService(storage_dir=storage_dir, device="cpu")
    set_diffrhythm_service(service)
    
    # Start model preload in background to keep app responsive
    import asyncio
    preload_task = asyncio.create_task(
        service.initialize(preload=True),
        name="model-preload"
    )
    
    # Don't await here - let the app start serving while model loads
    logger.info(f"DiffRhythm service initialized (storage: {storage_dir}), model preload started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DiffRhythm service...")
    # Cancel preload task if still running
    if not preload_task.done():
        preload_task.cancel()
        try:
            await preload_task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application"""
    # Create FastAPI app
    app = FastAPI(
        title="DiffRhythm Generation API",
        description="Direct prompt → track music generation with audio export",
        version="1.0.0",
        lifespan=lifespan
    )
    
# Configure CORS (разрешить все источники для локальной разработки)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Разрешить все источники
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(generation.router)
    
    # Mount static files for audio output
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)
    try:
        app.mount("/output", StaticFiles(directory=output_dir, check_dir=True), name="output")
        logger.info(f"Static files mounted at /output -> {output_dir}")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "DiffRhythm Generation API",
            "version": "1.0.0",
            "status": "running"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            return {
                "status": "healthy",
                "service": "DiffRhythm Generation API",
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Service unhealthy")
    
    return app


# Create FastAPI app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        log_level="info"
    )
