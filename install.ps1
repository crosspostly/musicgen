# MusicGen Local - Windows Installation Script
# Supports: Windows 10/11 (Native or WSL)
# Run as: powershell -ExecutionPolicy Bypass -File install.ps1

param(
    [switch]$UseWSL = $false
)

# Colors
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Status {
    param([string]$Message, [string]$Color = $Green)
    Write-Host "$Color✓ $Message$Reset"
}

function Write-Error {
    param([string]$Message)
    Write-Host "${Red}✗ $Message$Reset"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "${Yellow}⚠ $Message$Reset"
}

function Write-Info {
    param([string]$Message)
    Write-Host "${Yellow}$Message$Reset"
}

# Header
Write-Host ""
Write-Host "${Blue}╔════════════════════════════════════════╗$Reset"
Write-Host "${Blue}║   MusicGen Local - Windows Setup       ║$Reset"
Write-Host "${Blue}╚════════════════════════════════════════╝$Reset"
Write-Host ""

# Check if running with admin privileges
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Warning "For best results, run PowerShell as Administrator"
    Write-Info "Many installations require admin privileges"
}

# Check Python
Write-Info "Checking Python..."
$PythonPath = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if ($PythonPath) {
    $PythonVersion = & python.exe --version 2>&1
    Write-Status "Python $PythonVersion found"
} else {
    Write-Error "Python 3.9+ not found"
    Write-Info "Download from https://python.org"
    Write-Info "Or install with: winget install Python.Python.3.11"
    exit 1
}

# Check Redis
Write-Info "Checking Redis..."
$RedisPath = (Get-Command redis-server.exe -ErrorAction SilentlyContinue).Source
if ($RedisPath) {
    Write-Status "Redis found"
} else {
    Write-Warning "Redis not found"
    Write-Info "Option 1 (Native): winget install Redis.Redis"
    Write-Info "Option 2 (WSL): Use WSL with: wsl redis-server"
    Write-Info "Option 3 (Docker): docker run -d -p 6379:6379 redis:latest"
    Write-Info ""
    Write-Info "Install Redis and try again, or use Docker"
}

# Check FFmpeg
Write-Info "Checking FFmpeg..."
$FFmpegPath = (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue).Source
if ($FFmpegPath) {
    Write-Status "FFmpeg found"
} else {
    Write-Error "FFmpeg not found"
    Write-Info "Install with: winget install FFmpeg"
    exit 1
}

Write-Host ""

# Check Node.js (optional)
Write-Info "Checking Node.js (optional, for frontend development)..."
$NodePath = (Get-Command node.exe -ErrorAction SilentlyContinue).Source
if ($NodePath) {
    $NodeVersion = & node.exe --version 2>&1
    Write-Status "Node.js $NodeVersion found"
    $InstallFrontend = $true
} else {
    Write-Warning "Node.js not found (optional, only needed for development)"
    Write-Info "Download from https://nodejs.org"
    Write-Info "Or install with: winget install OpenJS.NodeJS"
    $InstallFrontend = $false
}

Write-Host ""

# Setup Python virtual environment
Write-Info "Setting up Python environment..."
$VenvDir = "venv"
if (-not (Test-Path $VenvDir)) {
    & python.exe -m venv $VenvDir
    Write-Status "Virtual environment created"
} else {
    Write-Status "Virtual environment already exists"
}

# Activate venv
$VenvActivate = "$VenvDir\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    & $VenvActivate
    Write-Status "Virtual environment activated"
} else {
    Write-Error "Could not activate virtual environment"
    exit 1
}

# Upgrade pip
Write-Info "Upgrading pip..."
& python.exe -m pip install --upgrade pip | Out-Null
Write-Status "Pip upgraded"

# Install Python dependencies
Write-Info "Installing Python dependencies..."
if (Test-Path "requirements.txt") {
    & pip install -r requirements.txt
    Write-Status "Python packages installed"
} else {
    Write-Error "requirements.txt not found"
    exit 1
}

Write-Host ""

# Install frontend dependencies (optional)
if ($InstallFrontend) {
    Write-Info "Installing frontend dependencies..."
    & npm install
    Write-Status "Frontend packages installed"
    Write-Host ""
}

# Create .env if not exists
Write-Info "Checking environment configuration..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Status ".env created from .env.example"
} else {
    Write-Status ".env already exists"
}

Write-Host ""
Write-Host "${Blue}╔════════════════════════════════════════╗$Reset"
Write-Host "${Blue}║       Installation Successful! 🎉      ║$Reset"
Write-Host "${Blue}╚════════════════════════════════════════╝$Reset"
Write-Host ""

Write-Info "Start services in separate terminals:"
Write-Host ""
Write-Info "Terminal 1 - Redis (job queue):"
Write-Info "  If installed locally:"
Write-Host "${Blue}  redis-server$Reset"
Write-Info "  Or via WSL:"
Write-Host "${Blue}  wsl redis-server$Reset"
Write-Info "  Or via Docker:"
Write-Host "${Blue}  docker run -d -p 6379:6379 redis:latest$Reset"
Write-Host ""

Write-Info "Terminal 2 - Python backend:"
Write-Host "${Blue}  $VenvDir\Scripts\Activate.ps1$Reset"
Write-Host "${Blue}  python -m uvicorn python.app.main:app --reload --host 0.0.0.0 --port 8000$Reset"
Write-Host ""

if ($InstallFrontend) {
    Write-Info "Terminal 3 - Frontend dev server:"
    Write-Host "${Blue}  npm run dev$Reset"
    Write-Host ""
    Write-Info "Or build for production:"
    Write-Host "${Blue}  npm run build$Reset"
    Write-Host "${Blue}  python -m http.server 3000 --directory dist$Reset"
    Write-Host ""
}

Write-Info "Then open:"
Write-Host "${Blue}  http://localhost:3000$Reset"
Write-Host ""

Write-Info "For Docker, use:"
Write-Host "${Blue}  docker-compose up$Reset"
Write-Host ""
