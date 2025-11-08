# E2E Testing Guide

Comprehensive guide for running and maintaining end-to-end tests for the DiffRhythm AI Music Generator.

## Overview

The E2E test suite validates the complete workflow across all three services:
- **Python DiffRhythm Service** (port 8000) - FastAPI service for music generation
- **Node.js Backend** (port 3001) - Express orchestration layer with SQLite persistence
- **React Frontend** (port 3000) - Vite-powered user interface

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Understanding Test Output](#understanding-test-output)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Writing New Tests](#writing-new-tests)
- [CI/CD Integration](#cicd-integration)

## Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Node.js 18+**
   ```bash
   node --version
   ```

3. **npm**
   ```bash
   npm --version
   ```

4. **FFmpeg** (for audio processing)
   ```bash
   ffmpeg -version
   ```
   
   Installation:
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

5. **SQLite3** (optional, for database inspection)
   ```bash
   sqlite3 --version
   ```

### Python Dependencies

Install Python dependencies including test packages:
```bash
pip install -r requirements.txt
```

Key test dependencies:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `requests` - HTTP client for API testing

### Node.js Dependencies

Install all Node.js dependencies:
```bash
npm install        # Root and frontend dependencies
npm install --workspace=backend  # Backend dependencies
```

## Quick Start

### 1. Run All E2E Tests

```bash
npm run test:e2e
```

This command will:
1. Check all dependencies
2. Build the frontend (if needed)
3. Clean up previous test artifacts
4. Start all three services
5. Run all E2E tests
6. Stop all services and save logs
7. Report results

### 2. Run Specific Test Categories

**Happy Path Tests Only:**
```bash
npm run test:e2e:happy
```

**Error Case Tests Only:**
```bash
npm run test:e2e:errors
```

### 3. Run Specific Test File

```bash
pytest tests/e2e/test_happy_path.py -v
```

### 4. Run Specific Test Function

```bash
pytest tests/e2e/test_happy_path.py::test_complete_workflow -v
```

## Test Structure

```
tests/e2e/
├── __init__.py              # Package initialization
├── pytest.ini               # Pytest configuration
├── conftest.py              # Test fixtures and service orchestration
├── test_happy_path.py       # Happy path workflow tests
├── test_error_cases.py      # Error handling and edge cases
├── run_tests.sh             # Test runner script
└── artifacts/               # Test artifacts (logs, generated files)
    ├── python_service.log
    ├── backend_service.log
    └── frontend_service.log
```

### Key Files

#### `conftest.py`
Contains pytest fixtures and the `ServiceOrchestrator` class that manages:
- Service lifecycle (start/stop)
- Port availability checks
- Health check polling
- Directory setup and cleanup
- Log collection

#### `test_happy_path.py`
Tests the complete successful workflow:
- Port availability verification
- Job creation and submission
- Status polling until completion
- Audio file validation (WAV/MP3)
- Database persistence verification
- Multiple format exports

#### `test_error_cases.py`
Tests error handling and edge cases:
- Invalid duration (too short/long)
- Missing required fields
- Invalid language codes
- Non-existent job queries
- Malformed JSON requests
- Concurrent job handling
- Health check structures
- Minimum valid duration edge case

## Running Tests

### Using npm Scripts (Recommended)

```bash
# Run all E2E tests
npm run test:e2e

# Run only happy path tests
npm run test:e2e:happy

# Run only error case tests
npm run test:e2e:errors
```

### Using pytest Directly

```bash
# Run all E2E tests with verbose output
pytest tests/e2e -v -m e2e

# Run with specific markers
pytest tests/e2e -v -m happy_path
pytest tests/e2e -v -m error_case

# Run with detailed output
pytest tests/e2e -v --tb=long --capture=no

# Run with test filtering
pytest tests/e2e -k "test_complete_workflow"

# Run with specific log level
pytest tests/e2e -v --log-cli-level=DEBUG
```

### Common pytest Options

- `-v` / `--verbose`: Verbose output
- `-s` / `--capture=no`: Don't capture output (see print statements)
- `--tb=short`: Short traceback format
- `--tb=long`: Long traceback format
- `-x` / `--exitfirst`: Exit on first failure
- `--maxfail=N`: Exit after N failures
- `-k EXPRESSION`: Filter tests by expression
- `-m MARKER`: Run tests with specific marker
- `--collect-only`: Show what tests would run without running them

## Understanding Test Output

### Successful Test Run

```
================================ test session starts =================================
tests/e2e/test_happy_path.py::test_complete_workflow PASSED                    [100%]

================================================================================
Step 1: Verifying service accessibility
================================================================================
✓ Frontend accessible on port 3000
✓ Backend accessible on port 3001
✓ Python service accessible on port 8000

================================================================================
Step 2: Creating DiffRhythm job
================================================================================
✓ Job created with ID: 12345678-1234-1234-1234-123456789abc

... (more steps)

================================= 1 passed in 45.23s =================================
```

### Failed Test Run

```
================================ FAILURES =========================================
___________________________ test_complete_workflow _______________________________

    def test_complete_workflow(...):
        response = requests.post(...)
>       assert response.status_code == 200
E       AssertionError: assert 500 == 200

tests/e2e/test_happy_path.py:42: AssertionError
================================= 1 failed in 10.52s =================================
```

When tests fail, check:
1. Service logs in `tests/e2e/artifacts/`
2. Test output for assertion details
3. Network connectivity between services
4. Port availability

## Configuration

### Service Ports

Default ports are defined in `tests/e2e/conftest.py`:
```python
PYTHON_SERVICE_PORT = 8000
BACKEND_SERVICE_PORT = 3001
FRONTEND_SERVICE_PORT = 3000
```

### Timeouts

Configured in `tests/e2e/conftest.py`:
- Health check timeout: 60 seconds
- Job completion timeout: 120 seconds
- Service stop timeout: 5 seconds

To adjust, modify the constants in test files or conftest.py.

### Test Data Directories

E2E tests use isolated temporary directories:
- **Storage**: `tmp/e2e/storage/` - Generated audio files
- **Database**: `tmp/e2e/storage/database.sqlite` - SQLite database
- **Logs**: `tmp/e2e/logs/` - Service logs
- **Artifacts**: `tests/e2e/artifacts/` - Copied logs for inspection

These directories are automatically cleaned before each test run.

### Environment Variables

The E2E orchestrator sets these environment variables for services:

**Python Service:**
```bash
STORAGE_DIR=tmp/e2e/storage
DATABASE_PATH=tmp/e2e/storage/python_database.sqlite
PYTHONUNBUFFERED=1
```

**Backend Service:**
```bash
NODE_ENV=test
PORT=3001
PY_DIFFRHYTHM_URL=http://localhost:8000
STORAGE_DIR=tmp/e2e/storage
DATABASE_PATH=tmp/e2e/storage/database.sqlite
FFMPEG_PATH=ffmpeg
```

**Frontend Service:**
```bash
PORT=3000
```

## Troubleshooting

### Port Already in Use

**Symptom:**
```
RuntimeError: Cannot start services: Ports in use: Python service (port 8000)
```

**Solution:**
1. Find and kill processes using the ports:
   ```bash
   # Find process using port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Or for all ports
   lsof -ti:8000,3001,3000 | xargs kill -9
   ```

2. Check no services are running:
   ```bash
   ps aux | grep -E "uvicorn|node.*index.js|vite"
   ```

### Service Failed to Start

**Symptom:**
```
RuntimeError: Python service failed to start. Logs:
...
```

**Solution:**
1. Check service logs in `tests/e2e/artifacts/`
2. Verify dependencies are installed:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
3. Check FFmpeg is installed:
   ```bash
   ffmpeg -version
   ```
4. Try starting service manually:
   ```bash
   cd python && python services/diffrhythm_service.py
   ```

### Frontend Build Issues

**Symptom:**
```
RuntimeError: Frontend build failed
```

**Solution:**
1. Manually build frontend:
   ```bash
   npm run build:frontend
   ```
2. Check build output for errors
3. Verify all frontend dependencies are installed:
   ```bash
   npm install
   ```

### Test Timeout

**Symptom:**
```
pytest: Job did not complete within 120 seconds
```

**Solution:**
1. Increase timeout in test file (look for `max_wait_time`)
2. Check Python service logs for processing issues
3. Verify system has sufficient resources (CPU/RAM)
4. Use shorter test durations (e.g., 10 seconds instead of 30)

### Database Lock Issues

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
1. Ensure all services are stopped:
   ```bash
   pkill -f "python.*diffrhythm"
   pkill -f "node.*index.js"
   ```
2. Remove test database:
   ```bash
   rm -rf tmp/e2e
   ```
3. Run tests again

### Connection Refused

**Symptom:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Solution:**
1. Check service is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check firewall settings
3. Verify service started successfully (check logs)
4. Increase health check timeout in conftest.py

## Writing New Tests

### Test Template

```python
import pytest
import requests

@pytest.mark.e2e
@pytest.mark.happy_path  # or error_case
def test_my_feature(backend_service_url, storage_dir):
    """
    Test description.
    """
    print("\n" + "=" * 80)
    print("Test: My Feature")
    print("=" * 80)
    
    # Your test code here
    response = requests.get(f"{backend_service_url}/api/endpoint")
    assert response.status_code == 200
    
    print("✓ Test passed")
    print("=" * 80)
```

### Available Fixtures

- `orchestrator` - ServiceOrchestrator instance
- `python_service_url` - Python service URL (http://localhost:8000)
- `backend_service_url` - Backend service URL (http://localhost:3001)
- `frontend_service_url` - Frontend service URL (http://localhost:3000)
- `storage_dir` - Storage directory Path object
- `database_path` - Database file Path object

### Best Practices

1. **Use markers**: Tag tests with `@pytest.mark.e2e` and category markers
2. **Clear output**: Use print statements to show test progress
3. **Assert early**: Fail fast on unexpected conditions
4. **Clean data**: Don't rely on data from other tests
5. **Timeouts**: Set reasonable timeouts for network requests
6. **Error messages**: Provide clear assertion messages
7. **Cleanup**: Let fixtures handle cleanup, don't manually stop services

### Test Markers

Available markers (defined in pytest.ini):
- `@pytest.mark.e2e` - All E2E tests
- `@pytest.mark.happy_path` - Happy path workflow tests
- `@pytest.mark.error_case` - Error and edge case tests
- `@pytest.mark.slow` - Tests that take a long time

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install FFmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install
          npm install --workspace=backend
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload test artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-artifacts
          path: tests/e2e/artifacts/
```

### Running in Docker

See `docker-compose.yml` for container-based testing setup.

## Performance Considerations

### Test Duration

- **Happy path tests**: ~45-60 seconds per test
- **Error case tests**: ~5-15 seconds per test
- **Full suite**: ~3-5 minutes

### Resource Usage

- **CPU**: Moderate (music generation is CPU-intensive)
- **Memory**: ~500MB-1GB for all services
- **Disk**: ~50-100MB per test run (audio files + logs)

### Optimization Tips

1. **Use shorter durations**: Test with 10-15 second clips instead of 30+ seconds
2. **Run in parallel**: Use pytest-xdist for parallel execution
3. **Skip slow tests**: Use `-m "not slow"` to skip marked tests
4. **Reuse builds**: Don't rebuild frontend for every test run

## Maintenance

### Regular Tasks

1. **Update dependencies**: Keep test dependencies current
2. **Review timeouts**: Adjust as needed for different environments
3. **Check logs**: Regularly review test artifacts for warnings
4. **Add tests**: Cover new features with E2E tests
5. **Cleanup**: Periodically remove old tmp/e2e directories

### Monitoring

Key metrics to track:
- Test duration trends
- Failure rates
- Service startup times
- Resource utilization

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review service logs in `tests/e2e/artifacts/`
3. Check existing GitHub issues
4. Create a new issue with:
   - Test command used
   - Error output
   - Service logs
   - System information

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Express Testing](https://expressjs.com/en/guide/testing.html)
