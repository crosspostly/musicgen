#!/bin/bash

# Development startup script for AI Music Generator
# Starts frontend, backend, and Python DiffRhythm service

set -e

echo "🚀 Starting AI Music Generator Development Environment"
echo "=================================================="

# Check if required tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "🔍 Checking required tools..."
check_command "node"
check_command "npm"
check_command "python3"
check_command "pip"

# Check if FFmpeg is installed (required for Python service)
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Audio conversion will fail."
    echo "   Please install FFmpeg: https://ffmpeg.org/download.html"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output
mkdir -p data
mkdir -p temp
mkdir -p python/models/cache
mkdir -p storage

# Install dependencies if needed
echo "📦 Installing dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

if [ ! -d "backend/node_modules" ]; then
    echo "Installing backend dependencies..."
    cd backend && npm install && cd ..
fi

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f "venv/pyvenv.cfg" ] || ! pip list | grep -q "fastapi"; then
    echo "Installing Python dependencies..."
    pip install -r python/requirements.txt
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

echo ""
echo "🎯 Starting services..."
echo "===================="

# Function to kill all background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Python DiffRhythm service
echo "🐍 Starting DiffRhythm Python service (port 8000)..."
cd python
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
PYTHON_PID=$!
cd ..

# Wait a moment for Python service to start
sleep 3

# Start Node.js backend
echo "🔧 Starting Node.js backend (port 3001)..."
cd backend
npm run dev &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting React frontend (port 3000)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ All services started!"
echo "======================"
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend:      http://localhost:3001"
echo "🐍 Python API:   http://localhost:8000"
echo "📊 Health checks:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend:      http://localhost:3001/health"
echo "   Python:       http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait