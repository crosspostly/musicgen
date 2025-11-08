#!/bin/bash
# E2E Test Runner Script
# Runs end-to-end tests with proper environment setup and cleanup

set -e

echo "=============================================="
echo "E2E Test Suite for DiffRhythm AI Music Generator"
echo "=============================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Check dependencies
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg not found. Audio export may fail."
fi

if ! command -v sqlite3 &> /dev/null; then
    echo "⚠️  Warning: sqlite3 not found. Database inspection may be limited."
fi

echo "✓ Core dependencies found"
echo ""

# Check Python packages
echo "Checking Python packages..."
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "Installing Python test dependencies..."
    pip install pytest pytest-asyncio requests
fi
echo "✓ Python packages ready"
echo ""

# Check Node packages
echo "Checking Node.js packages..."
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

if [ ! -d "backend/node_modules" ]; then
    echo "Installing backend dependencies..."
    cd backend && npm install && cd ..
fi
echo "✓ Node.js packages ready"
echo ""

# Build frontend if needed
echo "Checking frontend build..."
if [ ! -d "dist" ]; then
    echo "Building frontend for preview mode..."
    npm run build:frontend
fi
echo "✓ Frontend build ready"
echo ""

# Clean up any existing test artifacts
echo "Cleaning up previous test artifacts..."
rm -rf tmp/e2e
rm -rf tests/e2e/artifacts/*
echo "✓ Cleanup complete"
echo ""

# Run tests
echo "=============================================="
echo "Running E2E Tests"
echo "=============================================="
echo ""

# Set Python path to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run pytest with E2E tests
cd "$PROJECT_ROOT"
pytest tests/e2e \
    -v \
    --tb=short \
    --color=yes \
    -m e2e \
    "$@"

TEST_EXIT_CODE=$?

echo ""
echo "=============================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All E2E tests passed!"
else
    echo "✗ Some E2E tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo "=============================================="
echo ""

# Show artifacts location
if [ -d "tests/e2e/artifacts" ] && [ "$(ls -A tests/e2e/artifacts)" ]; then
    echo "Test artifacts available at: tests/e2e/artifacts/"
    ls -lh tests/e2e/artifacts/
fi

exit $TEST_EXIT_CODE
