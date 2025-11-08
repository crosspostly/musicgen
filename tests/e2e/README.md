# E2E Test Suite - Quick Reference

End-to-end tests for DiffRhythm AI Music Generator.

## Quick Start

```bash
# Run all E2E tests
npm run test:e2e

# Run happy path tests only
npm run test:e2e:happy

# Run error case tests only
npm run test:e2e:errors
```

## What Gets Tested

### Services
- ✅ Python DiffRhythm Service (port 8000)
- ✅ Node.js Backend (port 3001)
- ✅ React Frontend (port 3000)

### Workflows
- ✅ Complete job creation → processing → completion flow
- ✅ Audio file generation (WAV and MP3)
- ✅ Database persistence (SQLite)
- ✅ Status polling and progress tracking
- ✅ Error handling (invalid inputs, missing fields, etc.)
- ✅ Concurrent job handling
- ✅ Health check endpoints

## Prerequisites

- Python 3.8+
- Node.js 18+
- FFmpeg (for audio processing)
- SQLite3 (optional, for inspection)

Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

## Test Structure

```
tests/e2e/
├── conftest.py           # Service orchestration fixtures
├── test_happy_path.py    # Complete workflow tests
├── test_error_cases.py   # Error handling tests
├── run_tests.sh          # Test runner script
└── artifacts/            # Logs and outputs (created during tests)
```

## Common Commands

```bash
# Run specific test file
pytest tests/e2e/test_happy_path.py -v

# Run specific test
pytest tests/e2e/test_happy_path.py::test_complete_workflow -v

# Run with detailed output
pytest tests/e2e -v --capture=no

# Run with markers
pytest tests/e2e -v -m happy_path
pytest tests/e2e -v -m error_case
```

## Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports 8000, 3001, 3000
lsof -ti:8000,3001,3000 | xargs kill -9
```

### Clean Test Environment
```bash
# Remove test artifacts
rm -rf tmp/e2e tests/e2e/artifacts/*
```

### Manual Service Start
```bash
# Test Python service
cd python && python services/diffrhythm_service.py

# Test backend service
cd backend && npm run dev

# Test frontend
npm run preview
```

## Test Output

Tests create artifacts in:
- `tests/e2e/artifacts/` - Service logs
- `tmp/e2e/storage/` - Generated audio files
- `tmp/e2e/storage/database.sqlite` - Test database

These are automatically cleaned before each run.

## Documentation

See [docs/E2E-TESTING.md](../../docs/E2E-TESTING.md) for comprehensive documentation including:
- Detailed setup instructions
- Configuration options
- Writing new tests
- CI/CD integration
- Performance optimization

## Test Coverage

### Happy Path Tests
- ✅ Complete workflow (job creation → audio export → database)
- ✅ Port availability checks
- ✅ Audio format export (WAV/MP3)

### Error Case Tests
- ✅ Invalid duration (too short/long)
- ✅ Missing required fields
- ✅ Invalid language codes
- ✅ Non-existent job queries
- ✅ Malformed JSON requests
- ✅ Concurrent job handling
- ✅ Health check structures
- ✅ Edge cases (minimum valid duration)
- ✅ Non-existent API endpoints

## Tips

1. **First run builds frontend** - This takes extra time
2. **Tests clean up automatically** - No manual cleanup needed
3. **Logs are saved** - Check `tests/e2e/artifacts/` if tests fail
4. **Use shorter durations** - Test with 10-15 second clips
5. **Run specific tests** - Use `-k` or markers to filter tests

## CI/CD

Tests are designed to run in CI/CD pipelines. See CI configuration in `.github/workflows/` for integration examples.

## Support

Issues? Check:
1. [Troubleshooting section](#troubleshooting) above
2. Service logs in `tests/e2e/artifacts/`
3. [Full documentation](../../docs/E2E-TESTING.md)
