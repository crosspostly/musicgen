"""
E2E Test Fixtures and Service Orchestration

This module provides pytest fixtures for starting, managing, and cleaning up
all services required for end-to-end testing.
"""

import os
import sys
import time
import signal
import socket
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import pytest
import requests

logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
E2E_TEST_ROOT = PROJECT_ROOT / "tests" / "e2e"
E2E_ARTIFACTS_DIR = E2E_TEST_ROOT / "artifacts"
E2E_TMP_DIR = PROJECT_ROOT / "tmp" / "e2e"

# Service ports
PYTHON_SERVICE_PORT = 8000
BACKEND_SERVICE_PORT = 3001
FRONTEND_SERVICE_PORT = 3000

# Service URLs
PYTHON_SERVICE_URL = f"http://localhost:{PYTHON_SERVICE_PORT}"
BACKEND_SERVICE_URL = f"http://localhost:{BACKEND_SERVICE_PORT}"
FRONTEND_SERVICE_URL = f"http://localhost:{FRONTEND_SERVICE_PORT}"


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False


def wait_for_port_free(port: int, timeout: int = 10) -> bool:
    """Wait for a port to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_available(port):
            return True
        time.sleep(0.5)
    return False


def wait_for_health_check(url: str, timeout: int = 60) -> bool:
    """
    Wait for a service health check endpoint to respond with 200.
    
    Args:
        url: Health check URL
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if service is healthy, False otherwise
    """
    start_time = time.time()
    last_error = None
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                logger.info(f"✓ Health check passed: {url}")
                return True
            last_error = f"Status {response.status_code}"
        except requests.exceptions.RequestException as e:
            last_error = str(e)
        
        time.sleep(1)
    
    logger.error(f"✗ Health check failed: {url} - Last error: {last_error}")
    return False


class ServiceProcess:
    """Manages a subprocess for a service."""
    
    def __init__(self, name: str, process: subprocess.Popen, log_file: Path):
        self.name = name
        self.process = process
        self.log_file = log_file
    
    def stop(self):
        """Stop the service process gracefully."""
        if self.process and self.process.poll() is None:
            logger.info(f"Stopping {self.name}...")
            
            try:
                # Try graceful shutdown first
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    logger.warning(f"Force killing {self.name}...")
                    self.process.kill()
                    self.process.wait(timeout=2)
            except Exception as e:
                logger.error(f"Error stopping {self.name}: {e}")
            
            logger.info(f"✓ {self.name} stopped")
    
    def is_running(self) -> bool:
        """Check if the process is still running."""
        return self.process is not None and self.process.poll() is None
    
    def get_logs(self) -> str:
        """Get the service logs."""
        if self.log_file.exists():
            return self.log_file.read_text()
        return ""


class ServiceOrchestrator:
    """Orchestrates starting and stopping all services for E2E tests."""
    
    def __init__(self, tmp_dir: Path, artifacts_dir: Path):
        self.tmp_dir = tmp_dir
        self.artifacts_dir = artifacts_dir
        self.services: Dict[str, ServiceProcess] = {}
        
        # Setup directories
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories for E2E tests."""
        # Clean and create tmp directory
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create artifacts directory
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.tmp_dir / "storage").mkdir(exist_ok=True)
        (self.tmp_dir / "output").mkdir(exist_ok=True)
        (self.tmp_dir / "logs").mkdir(exist_ok=True)
        
        logger.info(f"✓ E2E directories created at {self.tmp_dir}")
    
    def check_ports_available(self) -> Tuple[bool, str]:
        """
        Check if all required ports are available.
        
        Returns:
            Tuple of (success, message)
        """
        ports = {
            "Python service": PYTHON_SERVICE_PORT,
            "Backend service": BACKEND_SERVICE_PORT,
            "Frontend service": FRONTEND_SERVICE_PORT,
        }
        
        unavailable = []
        for name, port in ports.items():
            if not is_port_available(port):
                unavailable.append(f"{name} (port {port})")
        
        if unavailable:
            return False, f"Ports in use: {', '.join(unavailable)}"
        return True, "All ports available"
    
    def start_python_service(self) -> ServiceProcess:
        """Start the Python DiffRhythm service."""
        logger.info("Starting Python DiffRhythm service...")
        
        python_dir = PROJECT_ROOT / "python"
        log_file = self.tmp_dir / "logs" / "python_service.log"
        
        env = os.environ.copy()
        env["STORAGE_DIR"] = str(self.tmp_dir / "storage")
        env["DATABASE_PATH"] = str(self.tmp_dir / "storage" / "python_database.sqlite")
        env["PYTHONUNBUFFERED"] = "1"
        
        with open(log_file, "w") as f:
            process = subprocess.Popen(
                [sys.executable, "services/diffrhythm_service.py"],
                cwd=python_dir,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
        
        service = ServiceProcess("Python service", process, log_file)
        self.services["python"] = service
        
        # Wait for service to be ready
        if not wait_for_health_check(f"{PYTHON_SERVICE_URL}/health", timeout=30):
            service.stop()
            raise RuntimeError(f"Python service failed to start. Logs:\n{service.get_logs()}")
        
        logger.info(f"✓ Python service started on port {PYTHON_SERVICE_PORT}")
        return service
    
    def start_backend_service(self) -> ServiceProcess:
        """Start the Node.js backend service."""
        logger.info("Starting Node.js backend service...")
        
        backend_dir = PROJECT_ROOT / "backend"
        log_file = self.tmp_dir / "logs" / "backend_service.log"
        
        env = os.environ.copy()
        env["NODE_ENV"] = "test"
        env["PORT"] = str(BACKEND_SERVICE_PORT)
        env["PY_DIFFRHYTHM_URL"] = PYTHON_SERVICE_URL
        env["STORAGE_DIR"] = str(self.tmp_dir / "storage")
        env["DATABASE_PATH"] = str(self.tmp_dir / "storage" / "database.sqlite")
        env["FFMPEG_PATH"] = "ffmpeg"
        
        with open(log_file, "w") as f:
            # Use npx tsx to run TypeScript directly
            process = subprocess.Popen(
                ["npx", "tsx", "src/index.ts"],
                cwd=backend_dir,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
        
        service = ServiceProcess("Backend service", process, log_file)
        self.services["backend"] = service
        
        # Wait for service to be ready
        if not wait_for_health_check(f"{BACKEND_SERVICE_URL}/api/health", timeout=30):
            service.stop()
            raise RuntimeError(f"Backend service failed to start. Logs:\n{service.get_logs()}")
        
        logger.info(f"✓ Backend service started on port {BACKEND_SERVICE_PORT}")
        return service
    
    def start_frontend_service(self) -> ServiceProcess:
        """Start the React frontend service in preview mode."""
        logger.info("Starting React frontend service...")
        
        frontend_dir = PROJECT_ROOT
        log_file = self.tmp_dir / "logs" / "frontend_service.log"
        
        # Build frontend first if dist doesn't exist
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            logger.info("Building frontend...")
            build_result = subprocess.run(
                ["npm", "run", "build:frontend"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if build_result.returncode != 0:
                raise RuntimeError(f"Frontend build failed:\n{build_result.stderr}")
        
        env = os.environ.copy()
        env["PORT"] = str(FRONTEND_SERVICE_PORT)
        
        with open(log_file, "w") as f:
            process = subprocess.Popen(
                ["npm", "run", "preview", "--", "--port", str(FRONTEND_SERVICE_PORT), "--host"],
                cwd=frontend_dir,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
        
        service = ServiceProcess("Frontend service", process, log_file)
        self.services["frontend"] = service
        
        # Wait for service to be ready (frontend doesn't have health endpoint, just check if port responds)
        if not wait_for_health_check(FRONTEND_SERVICE_URL, timeout=30):
            service.stop()
            raise RuntimeError(f"Frontend service failed to start. Logs:\n{service.get_logs()}")
        
        logger.info(f"✓ Frontend service started on port {FRONTEND_SERVICE_PORT}")
        return service
    
    def start_all_services(self):
        """Start all services in the correct order."""
        logger.info("=" * 80)
        logger.info("Starting all services for E2E tests")
        logger.info("=" * 80)
        
        # Check ports
        available, message = self.check_ports_available()
        if not available:
            raise RuntimeError(f"Cannot start services: {message}")
        logger.info(f"✓ {message}")
        
        try:
            # Start services in order: Python -> Backend -> Frontend
            self.start_python_service()
            self.start_backend_service()
            self.start_frontend_service()
            
            logger.info("=" * 80)
            logger.info("✓ All services started successfully!")
            logger.info(f"  Python service:   {PYTHON_SERVICE_URL}")
            logger.info(f"  Backend service:  {BACKEND_SERVICE_URL}")
            logger.info(f"  Frontend service: {FRONTEND_SERVICE_URL}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            self.stop_all_services()
            raise
    
    def stop_all_services(self):
        """Stop all running services."""
        logger.info("=" * 80)
        logger.info("Stopping all services")
        logger.info("=" * 80)
        
        # Stop in reverse order
        for service_name in ["frontend", "backend", "python"]:
            if service_name in self.services:
                self.services[service_name].stop()
                # Wait for port to be free
                if service_name == "python":
                    wait_for_port_free(PYTHON_SERVICE_PORT)
                elif service_name == "backend":
                    wait_for_port_free(BACKEND_SERVICE_PORT)
                elif service_name == "frontend":
                    wait_for_port_free(FRONTEND_SERVICE_PORT)
        
        # Copy logs to artifacts
        self.copy_logs_to_artifacts()
        
        logger.info("✓ All services stopped")
    
    def copy_logs_to_artifacts(self):
        """Copy service logs to artifacts directory."""
        logs_dir = self.tmp_dir / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                shutil.copy2(log_file, self.artifacts_dir / log_file.name)
            logger.info(f"✓ Logs copied to {self.artifacts_dir}")
    
    def get_storage_dir(self) -> Path:
        """Get the storage directory path."""
        return self.tmp_dir / "storage"
    
    def get_database_path(self) -> Path:
        """Get the database path."""
        return self.tmp_dir / "storage" / "database.sqlite"


@pytest.fixture(scope="session")
def orchestrator():
    """
    Pytest fixture that provides a ServiceOrchestrator for the entire test session.
    Starts all services before tests and stops them after.
    """
    orch = ServiceOrchestrator(E2E_TMP_DIR, E2E_ARTIFACTS_DIR)
    
    try:
        orch.start_all_services()
        yield orch
    finally:
        orch.stop_all_services()


@pytest.fixture(scope="session")
def python_service_url(orchestrator):
    """Get the Python service URL."""
    return PYTHON_SERVICE_URL


@pytest.fixture(scope="session")
def backend_service_url(orchestrator):
    """Get the backend service URL."""
    return BACKEND_SERVICE_URL


@pytest.fixture(scope="session")
def frontend_service_url(orchestrator):
    """Get the frontend service URL."""
    return FRONTEND_SERVICE_URL


@pytest.fixture(scope="session")
def storage_dir(orchestrator):
    """Get the storage directory path."""
    return orchestrator.get_storage_dir()


@pytest.fixture(scope="session")
def database_path(orchestrator):
    """Get the database path."""
    return orchestrator.get_database_path()
