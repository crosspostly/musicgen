# Testing Checklist - MVP Manual QA

This document provides a comprehensive manual testing checklist for the MusicGen AI MVP. Follow these steps to validate the complete workflow from prompt entry to audio download.

## Table of Contents

- [Pre-flight Checks](#pre-flight-checks)
- [Manual UI Testing](#manual-ui-testing)
- [API Spot Checks](#api-spot-checks)
- [Error Handling Verification](#error-handling-verification)
- [Output File Verification](#output-file-verification)

---

## Pre-flight Checks

Complete these setup steps before starting manual testing.

### ✓ Service Startup

1. **Ensure all three services are running:**

   ```bash
   # Terminal 1 - Python DiffRhythm Service (Port 8000)
   cd /path/to/musicgen
   source venv/bin/activate  # Activate Python virtual environment
   cd python && python services/diffrhythm_service.py
   # Expected output: "Uvicorn running on http://0.0.0.0:8000"
   ```

   ```bash
   # Terminal 2 - Node.js Backend (Port 3001)
   cd /path/to/musicgen/backend
   npm run dev
   # Expected output: "Express server running on port 3001"
   ```

   ```bash
   # Terminal 3 - React Frontend (Port 3000)
   cd /path/to/musicgen
   npm run dev
   # Expected output: "VITE v... ready in ... ms"
   ```

   **Alternative - Start all services at once:**
   ```bash
   ./start-dev.sh
   ```

2. **Verify all services are running:**

   - **Frontend**: http://localhost:3000 → Should display MeloGen AI interface
   - **Backend**: http://localhost:3001/health → Should return HTTP 200
   - **Python Service**: http://localhost:8000/health → Should return HTTP 200

3. **Confirm model preload initialization:**

   - Check Python service logs for: `"Model preload complete"` or similar initialization message
   - First generation request should NOT show model loading delay
   - Expected preload time: 10-30 seconds (one-time on startup)

4. **Verify output directory exists:**

   ```bash
   ls -la output/
   # Should be empty or contain previous test audio files
   ```

---

## Manual UI Testing

Complete the full MVP workflow through the web interface.

### Step 1: Navigate to DiffRhythm Generator

1. Open http://localhost:3000 in a web browser
2. Observe the "MeloGen AI" header with navigation options
3. Click on **DiffRhythm** model selection (marked with ⭐ star)
4. Verify the DiffRhythm Generator screen loads with:
   - "Генератор песен (DiffRhythm) ⭐" heading
   - Lyrics/text input textarea (pre-filled with sample text)
   - Three dropdowns: Genre, Mood, Gender
   - **"🎬 Генерировать песню"** (Generate Song) button

### Step 2: Enter Sample Prompt

1. Clear the lyrics textarea and enter sample text:
   ```
   Verse 1:
   This is a test song
   Testing the DiffRhythm generator
   
   Chorus:
   Testing, testing, one two three
   Everything working perfectly
   ```

2. Verify form fields have values:
   - **Genre**: Pop (default)
   - **Mood**: Happy (default)
   - **Gender**: Male (default)
   - **Lyrics**: Your entered text above

3. *Optional*: Change Genre to "Rock" or Mood to "Energetic" to test different configurations

### Step 3: Click Generate and Observe Loading State

1. Click the **"🎬 Генерировать песню"** button
2. Verify immediate UI changes:
   - Button becomes **disabled** (grayed out)
   - Button text changes to **"Генерация..."** (Generating...)
   - Status message appears: **"Ожидаем ответ от сервера... (до 120 сек)"**
   - Page shows loading indicator or visual feedback

3. Observe generation progress:
   - Should complete in approximately 10-30 seconds (faster if model preloaded)
   - No timeout errors should occur (120-second timeout available)

### Step 4: Audio Player Screen

1. After generation completes, verify the **Metadata Editor** screen appears with:
   - Audio player control visible
   - Play button (▶) and controls
   - Track duration displayed

2. **Play the generated audio:**
   - Click the play button
   - Audio should play for the expected duration
   - Volume slider should be functional
   - Playback should be smooth

3. Verify metadata fields:
   - Track name/title pre-filled
   - Duration displayed (should match generated audio length)

### Step 5: Navigate to Export/Download Screen

1. Click **"Continue to Export"** or similar button to proceed
2. Verify the **Export** screen displays:
   - Audio player with the generated track
   - **Download** button
   - File format options (MP3, WAV - if available)
   - Additional metadata (artist, album, genre - if editable)

### Step 6: Download Audio File

1. Click the **Download** button
2. Observe browser download dialog:
   - File should be named something like `track_*.mp3` or `track_*.wav`
   - File size should be reasonable (typically 500KB - 5MB for 30-second track)
   - Save the file to your local system

3. **Verify downloaded file:**

   ```bash
   # Check file was downloaded
   ls -lh ~/Downloads/track_*  # On macOS/Linux
   # or check Downloads folder in Windows/Explorer
   
   # Verify file is playable
   ffplay ~/Downloads/track_*.mp3  # Requires FFmpeg
   # or play with your system audio player
   ```

4. Confirm playback:
   - Audio plays without errors
   - Matches what you heard in the browser player

---

## API Spot Checks

Test the REST API endpoints directly using curl or Postman.

### Prerequisites

- Ensure all three services are running (see Pre-flight Checks)
- Have a terminal open or Postman/Insomnia installed

### 1. Health Checks

Verify services are available:

```bash
# Python service health
curl -X GET http://localhost:8000/health
# Expected response: {"status": "ok"} with HTTP 200

# Backend service health
curl -X GET http://localhost:3001/health
# Expected response: {"status": "ok"} with HTTP 200
```

### 2. POST /api/generate - Generate Music

Create a new track with a text prompt:

```bash
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Upbeat electronic dance music with synthesizers",
    "duration": 30
  }'

# Expected response (HTTP 201 Created):
# {
#   "track_id": "uuid-string",
#   "audio_url": "/output/track_uuid.mp3",
#   "duration": 30,
#   "device": "cpu",
#   "created_at": "2024-11-08T12:34:56Z"
# }
```

**Test variations:**

- **Default duration** (omit duration field):
  ```bash
  curl -X POST http://localhost:3001/api/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Simple test prompt"}'
  ```

- **Custom durations:**
  ```bash
  # 5 seconds (minimum)
  curl -X POST http://localhost:3001/api/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Short 5 second test", "duration": 5}'
  
  # 60 seconds
  curl -X POST http://localhost:3001/api/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "One minute test", "duration": 60}'
  
  # 300 seconds (5 minutes - maximum)
  curl -X POST http://localhost:3001/api/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Long five minute test", "duration": 300}'
  ```

### 3. GET /api/track/{track_id} - Retrieve Track Metadata

Fetch metadata for a generated track:

```bash
# Save the track_id from the generate response above
TRACK_ID="your-track-uuid-here"

curl -X GET http://localhost:3001/api/track/$TRACK_ID
# Expected response (HTTP 200 OK):
# {
#   "track_id": "uuid-string",
#   "prompt": "Upbeat electronic dance music with synthesizers",
#   "duration": 30,
#   "status": "completed",
#   "audio_url": "/output/track_uuid.mp3",
#   "file_size": 2048576,
#   "created_at": "2024-11-08T12:34:56Z"
# }
```

**Verify metadata:**

- `track_id` matches the generated track
- `prompt` contains your input text
- `duration` matches the requested duration
- `status` is `"completed"` or `"ready"`
- `audio_url` is valid and accessible
- `file_size` is positive (file exists)

### 4. Direct File Download via Audio URL

Test that generated audio files are accessible:

```bash
# Download the audio file directly
curl -X GET http://localhost:8000/output/track_uuid.mp3 -o test_audio.mp3
ls -lh test_audio.mp3

# Or use wget
wget http://localhost:8000/output/track_uuid.mp3 -O test_audio.mp3

# Verify with ffmpeg
ffprobe test_audio.mp3
# Should show: "Duration: 00:00:30" (or your specified duration)
```

---

## Error Handling Verification

Test error cases to ensure proper user messaging and graceful degradation.

### 1. Missing Prompt

**Expected Behavior**: Validation error with clear message

```bash
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"duration": 30}'

# Expected response (HTTP 400 Bad Request):
# {
#   "detail": "Missing required field: prompt"
# }
```

**UI Test**: Try to click Generate with empty lyrics field
- Expected: Error message appears below the button
- Message text: Clear and actionable (e.g., "Please enter lyrics or a prompt")

### 2. Empty Prompt String

```bash
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "", "duration": 30}'

# Expected response (HTTP 400 Bad Request):
# {
#   "detail": "Prompt cannot be empty"
# }
```

### 3. Duration Below Minimum (< 5 seconds)

```bash
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "duration": 3}'

# Expected response (HTTP 400 Bad Request):
# {
#   "detail": "Duration must be between 5 and 300 seconds"
# }
```

### 4. Duration Above Maximum (> 300 seconds)

```bash
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "duration": 400}'

# Expected response (HTTP 400 Bad Request):
# {
#   "detail": "Duration must be between 5 and 300 seconds"
# }
```

### 5. Invalid Track ID

```bash
curl -X GET http://localhost:3001/api/track/invalid-track-id-12345

# Expected response (HTTP 404 Not Found):
# {
#   "detail": "Track not found"
# }
```

### 6. Backend Service Unavailable

**Simulate backend failure:**

1. Stop the Node.js backend service (Ctrl+C in the backend terminal)
2. Try to generate audio through the UI or API

**Expected Behavior:**
- UI: Error message appears (e.g., "Cannot reach the server...")
- API: HTTP 503 or connection timeout
- User message: Clear indication to check backend status or retry

**Recovery:**
1. Restart the backend: `cd backend && npm run dev`
2. Wait 2 seconds for service to start
3. Retry generation - should succeed

### 7. Python Service Timeout

**Simulate timeout (optional - advanced test):**

```bash
# Create a very long prompt to increase generation time
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "This is an extremely long prompt that goes on and on and on with lots of detail to test how the system handles longer inputs and potentially slower generation times...",
    "duration": 300
  }'

# If it completes: Verify audio file was created
# If timeout (>120s): Should see timeout error message in UI
```

---

## Output File Verification

Verify that generated audio files are properly stored and accessible.

### 1. Check Output Directory Contents

```bash
# List all generated files
ls -lh output/

# Example output:
# -rw-r--r-- 1 user user 2.1M Nov  8 12:35 track_a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6.mp3
# -rw-r--r-- 1 user user 1.9M Nov  8 12:40 track_x1y2z3a4-b5c6-47d8-e9f0-a1b2c3d4e5f6.wav
```

**Verify:**
- Files exist with descriptive names
- File sizes are reasonable (>100KB for 30-second tracks)
- Timestamps are recent (from your test session)

### 2. Inspect Audio File Metadata

```bash
# Check first file with ffmpeg
ffprobe output/track_*.mp3 | head -20

# Expected output includes:
# Duration: 00:00:30.00
# Audio: mpeg3 float, 44100 Hz, mono, fltp, 128 kb/s
```

**Verify:**
- Duration matches the requested length (within 1-2 seconds tolerance)
- Sample rate is appropriate (44100 Hz or 48000 Hz)
- Bitrate is present (128kbps or higher for MP3)

### 3. Test Static File Serving

Verify files are accessible via HTTP:

```bash
# Get file size from the server
curl -I http://localhost:8000/output/track_*.mp3
# Look for: Content-Length header

# Download and play
curl -o /tmp/test.mp3 http://localhost:8000/output/track_*.mp3
ffplay /tmp/test.mp3
```

**Verify:**
- HTTP response is 200 OK
- Content-Type is `audio/mpeg` or `audio/wav`
- Content-Length matches actual file size
- File plays without corruption

### 4. Verify Database Persistence

Check that track records are stored:

```bash
# Connect to SQLite database
sqlite3 storage/database.sqlite

# List all generated tracks
SELECT track_id, prompt, duration, created_at FROM tracks LIMIT 5;

# Check job records
SELECT job_id, status, created_at FROM jobs LIMIT 5;

# Exit sqlite
.quit
```

**Verify:**
- Records exist for each generation attempt
- Timestamps are accurate
- Prompts are stored correctly
- Status is "completed" for successful generations

---

## Quick Reference - Common Test Scenarios

### Scenario 1: Happy Path (5 minutes)

1. ✓ Navigate to DiffRhythm generator
2. ✓ Enter sample prompt
3. ✓ Click Generate and wait for completion
4. ✓ Play audio in browser player
5. ✓ Download file and verify it plays locally

**Expected Result**: Audio file downloaded successfully

### Scenario 2: API Testing (10 minutes)

1. ✓ Health check endpoints
2. ✓ POST /api/generate with valid input
3. ✓ GET /api/track/{id} to retrieve metadata
4. ✓ Download audio file via HTTP
5. ✓ Verify file in output directory

**Expected Result**: All API calls succeed with proper responses

### Scenario 3: Error Cases (5 minutes)

1. ✓ Test empty prompt error
2. ✓ Test invalid duration bounds
3. ✓ Test invalid track ID (404)
4. ✓ Simulate backend unavailability
5. ✓ Verify error messages are user-friendly

**Expected Result**: All errors handled gracefully with clear messages

---

## Troubleshooting

### Issue: Python Service Won't Start

**Symptoms**: Port 8000 already in use or ModuleNotFoundError

```bash
# Kill existing process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Verify virtual environment
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Try starting again
cd python && python services/diffrhythm_service.py
```

### Issue: Backend Can't Connect to Python Service

**Symptoms**: Backend logs show "Connection refused" to localhost:8000

```bash
# Verify Python service is actually running
curl http://localhost:8000/health

# Check firewall rules
sudo ufw allow 8000

# Ensure .env is configured correctly
grep PY_DIFFRHYTHM_URL .env
# Should be: PY_DIFFRHYTHM_URL=http://localhost:8000
```

### Issue: Downloaded File Won't Play

**Symptoms**: Audio player shows error or file is 0 bytes

```bash
# Check file integrity
ffprobe ~/Downloads/track_*.mp3

# Verify file size is > 100KB
ls -lh ~/Downloads/track_*

# Try downloading via curl again
curl http://localhost:8000/output/track_*.mp3 -o fresh_download.mp3
ffplay fresh_download.mp3
```

### Issue: Generation Takes Too Long (>120 seconds)

**Symptoms**: Request timeout in browser UI

```bash
# Check Python service logs for errors
# Should see generation progress messages

# Verify system resources
top  # Check CPU/memory usage

# Try with shorter duration
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Short test", "duration": 5}'
```

---

## Test Sign-Off

Use this section to document your testing session:

```
Tester Name: ________________
Date: _______________________
Environment: 
  OS: ________________
  Python Version: ________________
  Node Version: ________________
  Browser: ________________

Tests Completed:
☐ Pre-flight checks passed
☐ Manual UI test (happy path)
☐ API spot checks passed
☐ Error handling verified
☐ Output files verified

Issues Found:
_________________________________
_________________________________

Overall Status: ☐ PASS  ☐ FAIL  ☐ PARTIAL
```

---

## Additional Resources

- **[README.md](../README.md)** - Project overview and quick start
- **[INSTALL.md](../INSTALL.md)** - Detailed installation instructions
- **[E2E-TESTING.md](./E2E-TESTING.md)** - Automated end-to-end testing guide
- **[CI-CD.md](./CI-CD.md)** - Continuous integration setup

---

**Last Updated**: November 2024  
**MVP Version**: 1.0  
**Status**: ✅ Comprehensive Testing Checklist Ready
