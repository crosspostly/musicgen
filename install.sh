#!/bin/bash

# MusicGen Local - Installation Script
# Supports: macOS, Linux (Ubuntu/Debian), WSL
# Usage: ./install.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.9"
NODE_MIN_VERSION="16"
VENV_DIR="venv"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MusicGen Local - Setup Installation  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    DISTRO=$(lsb_release -si 2>/dev/null || echo "linux")
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Detected OS: ${OS^^}${NC}"
echo ""

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_ge() {
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# Check Python
echo -e "${YELLOW}Checking Python...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
    
    if ! version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        echo -e "${RED}✗ Python ${PYTHON_MIN_VERSION}+ required (found ${PYTHON_VERSION})${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    if [ "$OS" = "macos" ]; then
        echo -e "${YELLOW}  Install with: brew install python@3.9${NC}"
    else
        echo -e "${YELLOW}  Install with: sudo apt install python3.9${NC}"
    fi
    exit 1
fi

# Check Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if command_exists redis-server; then
    REDIS_VERSION=$(redis-server --version 2>&1 | awk '{print $NF}')
    echo -e "${GREEN}✓ Redis ${REDIS_VERSION} found${NC}"
else
    echo -e "${RED}✗ Redis not found${NC}"
    if [ "$OS" = "macos" ]; then
        echo -e "${YELLOW}  Install with: brew install redis${NC}"
    else
        echo -e "${YELLOW}  Install with: sudo apt install redis-server${NC}"
    fi
    echo -e "${YELLOW}  (Redis is required for job queue)${NC}"
    exit 1
fi

# Check FFmpeg
echo -e "${YELLOW}Checking FFmpeg...${NC}"
if command_exists ffmpeg; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
    echo -e "${GREEN}✓ FFmpeg ${FFMPEG_VERSION} found${NC}"
else
    echo -e "${RED}✗ FFmpeg not found${NC}"
    if [ "$OS" = "macos" ]; then
        echo -e "${YELLOW}  Install with: brew install ffmpeg${NC}"
    else
        echo -e "${YELLOW}  Install with: sudo apt install ffmpeg${NC}"
    fi
    echo -e "${YELLOW}  (FFmpeg is required for audio processing)${NC}"
    exit 1
fi

echo ""

# Check Node.js (optional)
echo -e "${YELLOW}Checking Node.js (optional, for frontend development)...${NC}"
if command_exists node; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"
    INSTALL_FRONTEND=1
else
    echo -e "${YELLOW}⚠ Node.js not found (optional, only needed for development)${NC}"
    INSTALL_FRONTEND=0
fi

echo ""

# Setup Python virtual environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip >/dev/null 2>&1
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python packages installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

echo ""

# Install frontend dependencies (optional)
if [ $INSTALL_FRONTEND -eq 1 ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Frontend packages installed${NC}"
    echo ""
fi

# Create .env if not exists
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env created from .env.example${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Installation Successful! 🎉      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Start services in separate terminals:${NC}"
echo ""
echo -e "${GREEN}Terminal 1 - Redis (job queue):${NC}"
echo -e "  ${BLUE}redis-server${NC}"
echo ""
echo -e "${GREEN}Terminal 2 - Python backend:${NC}"
echo -e "  ${BLUE}source $VENV_DIR/bin/activate${NC}"
echo -e "  ${BLUE}python -m uvicorn python.app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
if [ $INSTALL_FRONTEND -eq 1 ]; then
    echo -e "${GREEN}Terminal 3 - Frontend dev server:${NC}"
    echo -e "  ${BLUE}npm run dev${NC}"
    echo ""
    echo -e "${GREEN}Or build for production:${NC}"
    echo -e "  ${BLUE}npm run build${NC}"
    echo -e "  ${BLUE}python -m http.server 3000 --directory dist${NC}"
    echo ""
fi

echo -e "${YELLOW}Then open:${NC}"
echo -e "  ${BLUE}http://localhost:3000${NC}"
echo ""

echo -e "${YELLOW}For Docker, use:${NC}"
echo -e "  ${BLUE}docker-compose up${NC}"
echo ""
