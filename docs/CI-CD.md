# CI/CD Pipeline Documentation

## Overview

This document describes the GitHub Actions CI/CD pipeline that automatically tests the Python backend, Node.js backend, and frontend components of the musicgen-local project.

## Pipeline Architecture

### Workflow File
- Location: `.github/workflows/ci.yml`
- Triggers: Push to main/develop branches and pull requests
- Jobs: Setup → Python Tests → Backend Tests → Frontend Tests → Coverage Report

### System Requirements for CI

The CI pipeline installs the following system dependencies:
- **FFmpeg**: For audio format conversion (MP3, WAV)
- **libsndfile1**: For audio file I/O operations

## Jobs Overview

### 1. Setup Job
**Purpose**: Cache dependencies for faster subsequent jobs

**Steps**:
- Setup Node.js v20 with npm cache
- Setup Python 3.11 with pip cache

**Duration**: ~30s

### 2. Python Tests Job
**Purpose**: Run Python test suite with coverage analysis

**Steps**:
1. Install system dependencies (FFmpeg, libsndfile1)
2. Install Python requirements
3. Run pytest with coverage:
   - Command: `pytest tests/ --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing`
   - Coverage reports generated in `python/htmlcov/` and `python/coverage.xml`
4. Verify audio artifacts are generated
5. Archive artifacts and coverage reports

**Coverage Output**:
- HTML Report: `python/htmlcov/index.html` (uploaded as artifact)
- XML Report: `python/coverage.xml` (for CI integrations)
- Console: Printed as `term-missing`

**Audio Artifacts**:
- Location: `python/tests/artifacts/`
- Formats: WAV, MP3
- Uploaded as: `python-audio-artifacts`

**Duration**: ~3-5 minutes (includes model loading)

### 3. Backend Tests Job
**Purpose**: Run Node.js backend tests with coverage

**Steps**:
1. Install dependencies
2. Run backend tests: `npm run test:backend -- --coverage`
3. Tests use Vitest with jsdom environment
4. Coverage reports generated in `backend/coverage/`

**Coverage Output**:
- HTML Report: `backend/coverage/index.html` (uploaded as artifact)
- JSON Report: `backend/coverage/coverage-final.json`

**Duration**: ~1-2 minutes

### 4. Frontend Tests Job
**Purpose**: Run frontend tests with coverage and build

**Steps**:
1. Install dependencies
2. Run frontend tests: `npm run test:frontend -- --coverage`
   - Tests in `screens/__tests__/**/*.test.tsx`
   - Tests in `services/__tests__/**/*.test.ts`
3. Build frontend: `npm run build:frontend`
4. Coverage reports generated in `coverage/coverage-frontend/`

**Coverage Output**:
- HTML Report: `coverage/coverage-frontend/index.html` (uploaded as artifact)
- Distribution Build: `dist/` (uploaded as artifact)

**Duration**: ~2-3 minutes

### 5. Coverage Report Job
**Purpose**: Aggregate and summarize coverage results

**Steps**:
1. Download all coverage artifacts
2. Generate summary in GitHub Actions step summary
3. Report which coverage types were generated

**Output**: Summary appended to workflow run summary

### 6. Verify Tests Job
**Purpose**: Ensure all tests passed

**Checks**: Verifies that all dependent jobs succeeded

## Local Development

### Prerequisites
```bash
# System dependencies
sudo apt-get install ffmpeg libsndfile1

# Node dependencies
npm install

# Python dependencies
pip install -r python/requirements.txt
```

### Running Tests Locally

#### Frontend Tests
```bash
# Single run with coverage
npm run test:frontend -- --coverage

# Watch mode (auto-rerun on changes)
npm run test:watch
```

#### Backend Tests
```bash
# Single run with coverage
npm run test:backend -- --coverage

# Watch mode
npm run test:backend -- --watch
```

#### Python Tests
```bash
# All tests with coverage
cd python && pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Specific test file
cd python && pytest tests/test_audio_export.py -v

# With markers
cd python && pytest -m "not slow" -v
```

#### All Tests Together
```bash
npm run test:all
```

### Test Files Location

```
project/
├── screens/__tests__/
│   └── *.test.tsx              # Frontend component tests
├── services/__tests__/
│   └── *.test.ts               # Frontend service tests
├── backend/src/
│   └── *.test.ts               # Backend API tests
└── python/tests/
    ├── test_audio_export.py    # Audio export integration tests
    ├── test_integration.py     # Job queue integration tests
    ├── test_job_queue.py       # Queue service tests
    ├── test_job_api.py         # Job API tests
    ├── test_database.py        # Database tests
    └── ...
```

## Coverage Configuration

### Frontend
- **Config**: `vite.config.ts` (test.coverage section)
- **Provider**: V8
- **Reports**: HTML, LCOV, text
- **Output Directory**: `coverage/coverage-frontend/`

### Backend
- **Config**: `backend/vitest.config.ts` (test.coverage section)
- **Provider**: V8
- **Reports**: HTML, LCOV, text
- **Output Directory**: `backend/coverage/`

### Python
- **Tool**: pytest-cov
- **Command**: `--cov=app --cov-report=html --cov-report=xml --cov-report=term-missing`
- **Output Directory**: `python/htmlcov/`

## Audio Artifacts

### Generation
Audio test artifacts are generated by `python/tests/test_audio_export.py` integration tests:
- **WAV files**: Raw PCM audio (44100 Hz, 16-bit)
- **MP3 files**: Compressed audio (192 kbps)
- **Location**: `python/tests/artifacts/`

### Download from CI
1. Go to GitHub Actions workflow run
2. Scroll to "Artifacts" section
3. Download `python-audio-artifacts` ZIP file
4. Extract and inspect WAV/MP3 files

### Manual Testing
```bash
cd python
# Run audio export tests specifically
pytest tests/test_audio_export.py -v

# Inspect generated files
ls -lah python/tests/artifacts/
file python/tests/artifacts/*.wav
file python/tests/artifacts/*.mp3
```

## Troubleshooting

### Python Tests Timeout
- Increase timeout in pytest.ini or command
- Python model loading can be slow (~1-2 min on first run)

### Audio Artifacts Not Generated
- Verify ffmpeg is installed: `ffmpeg -version`
- Verify libsndfile1 is installed: `apt-cache policy libsndfile1`
- Check test output for specific errors

### Backend Tests Failing
- Verify Node.js version: `node --version` (should be v20+)
- Clear node_modules: `rm -rf node_modules backend/node_modules && npm install`
- Check workspace linking: `npm ls --depth=0`

### Frontend Tests Failing
- Verify all dependencies installed: `npm install`
- Check React version compatibility
- Review test error messages for missing imports

### Coverage Not Generated
- Verify `@vitest/coverage-v8` is installed
- Check that test:coverage script is configured
- Review vitest config for coverage settings

## Environment Variables

### CI Environment
- `CI=true` - Automatically set by GitHub Actions
- `NODE_ENV=test` - Set for test runs
- `PYTHON_ENV=testing` - Set for Python tests

### Local Development
Create `.env.local` for local overrides:
```bash
VITE_API_URL=http://localhost:3001/api
VITE_BACKEND_URL=http://localhost:3001
```

## Performance Tips

### Caching
- npm cache is automatically managed by `actions/setup-node@v4`
- pip cache is automatically managed by `actions/setup-python@v5`
- Cache is keyed by dependency lock files

### Parallel Execution
- Backend, frontend, and Python tests run in parallel after setup
- Coverage aggregation runs after all tests complete

### Artifact Management
- Coverage reports retained for 30 days
- Build artifacts retained for 5 days
- Audio artifacts retained for 5 days

## Extending the Pipeline

### Adding New Tests
1. Create test file in appropriate `__tests__` directory
2. File naming: `*.test.ts`, `*.test.tsx`, or `*.test.py`
3. Tests are auto-discovered by Vitest/pytest
4. Coverage is automatically collected

### Adding New CI Jobs
1. Add new job to `.github/workflows/ci.yml`
2. Specify dependencies with `needs:`
3. Add artifact uploads if needed
4. Update summary in coverage-report job

### Custom Environment Variables
1. Add to job `env:` section or workflow `env:`
2. Reference as `${{ env.VAR_NAME }}` in steps
3. Or use repository/environment secrets

## Best Practices

1. **Commit Message**: Reference tests affected
   ```
   feat: add new feature
   - Add backend API test
   - Add frontend component test
   ```

2. **Test Coverage**: Aim for >80% coverage
   - Use coverage reports to identify gaps
   - Add tests for critical paths

3. **Test Performance**: Keep tests fast
   - Use mocking for external dependencies
   - Parallelize test execution
   - Use watch mode during development

4. **Artifact Inspection**: Review artifacts after failures
   - Download coverage reports
   - Check audio artifacts for quality
   - Verify build outputs

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vitest Documentation](https://vitest.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
