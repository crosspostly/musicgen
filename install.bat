@echo off
REM MusicGen Local - Windows Installation Script (Batch)
REM Supports: Windows 10/11
REM Run as: install.bat

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   MusicGen Local - Windows Setup
echo ========================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Download from https://python.org or run:
    echo   winget install Python.Python.3.11
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: %PYTHON_VERSION% found

REM Check Redis
echo Checking Redis...
redis-server --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Redis not found
    echo Install with: winget install Redis.Redis
    echo Or use WSL: wsl redis-server
    echo Or use Docker: docker run -d -p 6379:6379 redis:latest
)

REM Check FFmpeg
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: FFmpeg not found
    echo Install with: winget install FFmpeg
    exit /b 1
)
echo OK: FFmpeg found

REM Check Node.js (optional)
echo.
echo Checking Node.js (optional)...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Node.js not found (optional, only for development)
    echo Download from https://nodejs.org
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo OK: !NODE_VERSION! found
    set INSTALL_FRONTEND=1
)

echo.

REM Setup Python virtual environment
echo Setting up Python environment...
if not exist "venv\" (
    python -m venv venv
    echo OK: Virtual environment created
) else (
    echo OK: Virtual environment already exists
)

REM Install Python dependencies
echo Installing Python dependencies...
if exist "requirements.txt" (
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    echo OK: Python packages installed
) else (
    echo Error: requirements.txt not found
    exit /b 1
)

echo.

REM Install frontend dependencies (optional)
if defined INSTALL_FRONTEND (
    echo Installing frontend dependencies...
    call npm install
    echo OK: Frontend packages installed
    echo.
)

REM Create .env if not exists
echo Checking environment configuration...
if not exist ".env" (
    copy ".env.example" ".env"
    echo OK: .env created from .env.example
) else (
    echo OK: .env already exists
)

echo.
echo ========================================
echo   Installation Successful! [ok]
echo ========================================
echo.

echo Start services in separate terminals:
echo.
echo Terminal 1 - Redis (job queue):
echo   redis-server
echo   Or via Docker:
echo   docker run -d -p 6379:6379 redis:latest
echo.
echo Terminal 2 - Python backend:
echo   venv\Scripts\activate.bat
echo   python -m uvicorn python.app.main:app --reload --host 0.0.0.0 --port 8000
echo.
if defined INSTALL_FRONTEND (
    echo Terminal 3 - Frontend dev server:
    echo   npm run dev
    echo.
    echo Or build for production:
    echo   npm run build
    echo   python -m http.server 3000 --directory dist
    echo.
)
echo Then open: http://localhost:3000
echo.
echo For Docker, use: docker-compose up
echo.

pause
