"""
E2E Happy Path Tests

Tests the complete workflow from job creation to audio export across all services.
"""

import time
import sqlite3
from pathlib import Path
import pytest
import requests


@pytest.mark.e2e
@pytest.mark.happy_path
def test_complete_workflow(
    python_service_url,
    backend_service_url,
    frontend_service_url,
    storage_dir,
    database_path
):
    """
    Test the complete happy path workflow:
    1. Verify all services are accessible on their expected ports
    2. Create a DiffRhythm job via backend API
    3. Poll job status until completion
    4. Verify WAV and MP3 files are created
    5. Fetch result metadata from Python service
    6. Verify database persistence (jobs and tracks tables)
    """
    
    # Step 1: Verify all services are accessible
    print("\n" + "=" * 80)
    print("Step 1: Verifying service accessibility")
    print("=" * 80)
    
    # Check frontend (port 3000)
    response = requests.get(frontend_service_url, timeout=5)
    assert response.status_code == 200, f"Frontend not accessible: {response.status_code}"
    print(f"✓ Frontend accessible on port 3000")
    
    # Check backend health (port 3001)
    response = requests.get(f"{backend_service_url}/api/health", timeout=5)
    assert response.status_code == 200, f"Backend health check failed: {response.status_code}"
    print(f"✓ Backend accessible on port 3001")
    
    # Check Python service health (port 8000)
    response = requests.get(f"{python_service_url}/health", timeout=5)
    assert response.status_code == 200, f"Python service health check failed: {response.status_code}"
    health_data = response.json()
    assert health_data["status"] == "healthy"
    print(f"✓ Python service accessible on port 8000")
    
    # Step 2: Create a DiffRhythm job via backend API
    print("\n" + "=" * 80)
    print("Step 2: Creating DiffRhythm job")
    print("=" * 80)
    
    job_request = {
        "prompt": "Upbeat electronic dance music with energetic beats",
        "durationSeconds": 15,  # Short duration for faster testing
        "language": "en",
        "genre": "Electronic",
        "mood": "Energetic"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    assert response.status_code in [200, 201], f"Job creation failed: {response.status_code} - {response.text}"
    
    job_data = response.json()
    assert "jobId" in job_data or "job_id" in job_data
    job_id = job_data.get("jobId") or job_data.get("job_id")
    assert job_id is not None
    print(f"✓ Job created with ID: {job_id}")
    
    # Step 3: Poll job status until completion
    print("\n" + "=" * 80)
    print("Step 3: Polling job status until completion")
    print("=" * 80)
    
    max_wait_time = 120  # 2 minutes
    poll_interval = 2  # seconds
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < max_wait_time:
        response = requests.get(
            f"{backend_service_url}/api/jobs/diffrhythm/{job_id}",
            timeout=5
        )
        assert response.status_code == 200, f"Failed to get job status: {response.status_code}"
        
        status_data = response.json()
        current_status = status_data.get("status")
        current_progress = status_data.get("progress", 0)
        
        # Print progress updates
        if current_progress != last_progress:
            print(f"  Status: {current_status}, Progress: {current_progress}%")
            last_progress = current_progress
        
        if current_status == "completed":
            print(f"✓ Job completed in {time.time() - start_time:.1f} seconds")
            break
        
        if current_status == "failed":
            error = status_data.get("error", "Unknown error")
            pytest.fail(f"Job failed: {error}")
        
        time.sleep(poll_interval)
    else:
        pytest.fail(f"Job did not complete within {max_wait_time} seconds")
    
    # Step 4: Verify WAV and MP3 files are created
    print("\n" + "=" * 80)
    print("Step 4: Verifying audio files")
    print("=" * 80)
    
    # List files in storage directory
    storage_files = list(storage_dir.glob("*"))
    print(f"Storage directory contents: {[f.name for f in storage_files]}")
    
    # Check for audio files (they might be named with the Python job ID, not our local job ID)
    wav_files = list(storage_dir.glob("*.wav"))
    mp3_files = list(storage_dir.glob("*.mp3"))
    
    assert len(wav_files) > 0, f"No WAV files found in {storage_dir}"
    assert len(mp3_files) > 0, f"No MP3 files found in {storage_dir}"
    
    wav_file = wav_files[0]
    mp3_file = mp3_files[0]
    
    print(f"✓ WAV file found: {wav_file.name} ({wav_file.stat().st_size} bytes)")
    print(f"✓ MP3 file found: {mp3_file.name} ({mp3_file.stat().st_size} bytes)")
    
    # Verify file sizes are reasonable (not empty)
    assert wav_file.stat().st_size > 1000, "WAV file is too small"
    assert mp3_file.stat().st_size > 1000, "MP3 file is too small"
    
    # Step 5: Fetch result metadata from Python service
    print("\n" + "=" * 80)
    print("Step 5: Fetching track metadata")
    print("=" * 80)
    
    # Get tracks from backend
    response = requests.get(f"{backend_service_url}/api/tracks", timeout=5)
    assert response.status_code == 200, f"Failed to fetch tracks: {response.status_code}"
    
    tracks = response.json()
    assert len(tracks) > 0, "No tracks found in database"
    
    track = tracks[0]
    print(f"✓ Track found:")
    print(f"  ID: {track.get('id')}")
    print(f"  Duration: {track.get('duration')} seconds")
    print(f"  Model: {track.get('model')}")
    print(f"  Metadata: {track.get('metadata', {})}")
    
    # Verify track has required fields
    assert track.get("duration") is not None
    assert track.get("model") == "diffrhythm"
    
    # Step 6: Verify database persistence
    print("\n" + "=" * 80)
    print("Step 6: Verifying database persistence")
    print("=" * 80)
    
    # Connect to SQLite database and verify records
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Check jobs table
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE id = ?", (job_id,))
    job_count = cursor.fetchone()[0]
    assert job_count == 1, f"Expected 1 job record, found {job_count}"
    print(f"✓ Job record found in database")
    
    # Check job details
    cursor.execute(
        "SELECT type, status, progress FROM jobs WHERE id = ?",
        (job_id,)
    )
    job_row = cursor.fetchone()
    assert job_row[0] == "diffrhythm", f"Job type mismatch: {job_row[0]}"
    assert job_row[1] in ["completed", "processing"], f"Job status unexpected: {job_row[1]}"
    print(f"  Type: {job_row[0]}, Status: {job_row[1]}, Progress: {job_row[2]}")
    
    # Check tracks table
    cursor.execute("SELECT COUNT(*) FROM tracks WHERE job_id = ?", (job_id,))
    track_count = cursor.fetchone()[0]
    assert track_count >= 1, f"Expected at least 1 track record, found {track_count}"
    print(f"✓ Track record(s) found in database")
    
    # Check track details
    cursor.execute(
        "SELECT id, model, duration, file_path FROM tracks WHERE job_id = ? LIMIT 1",
        (job_id,)
    )
    track_row = cursor.fetchone()
    assert track_row is not None, "No track record found"
    print(f"  Track ID: {track_row[0]}")
    print(f"  Model: {track_row[1]}")
    print(f"  Duration: {track_row[2]}")
    print(f"  File path: {track_row[3]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ All workflow steps completed successfully!")
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.happy_path
def test_port_availability(python_service_url, backend_service_url, frontend_service_url):
    """
    Explicitly test that all services are running on their expected ports.
    """
    print("\n" + "=" * 80)
    print("Testing port availability")
    print("=" * 80)
    
    # Test Python service (port 8000)
    response = requests.get(f"{python_service_url}/health", timeout=5)
    assert response.status_code == 200
    print(f"✓ Python service responding on port 8000")
    
    # Test Backend service (port 3001)
    response = requests.get(f"{backend_service_url}/api/health", timeout=5)
    assert response.status_code == 200
    print(f"✓ Backend service responding on port 3001")
    
    # Test Frontend service (port 3000)
    response = requests.get(frontend_service_url, timeout=5)
    assert response.status_code == 200
    print(f"✓ Frontend service responding on port 3000")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.happy_path
def test_audio_format_export(python_service_url, backend_service_url, storage_dir):
    """
    Test that both WAV and MP3 formats are exported correctly.
    """
    print("\n" + "=" * 80)
    print("Testing audio format export")
    print("=" * 80)
    
    # Create a job
    job_request = {
        "prompt": "Calm piano melody",
        "durationSeconds": 10,
        "language": "en",
        "genre": "Classical",
        "mood": "Calm"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    assert response.status_code in [200, 201]
    job_id = response.json().get("jobId") or response.json().get("job_id")
    
    # Wait for completion
    max_wait = 120
    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = requests.get(f"{backend_service_url}/api/jobs/diffrhythm/{job_id}", timeout=5)
        status = response.json().get("status")
        if status == "completed":
            break
        if status == "failed":
            pytest.fail(f"Job failed: {response.json().get('error')}")
        time.sleep(2)
    else:
        pytest.fail("Job did not complete in time")
    
    # Verify both formats exist
    wav_files = list(storage_dir.glob("*.wav"))
    mp3_files = list(storage_dir.glob("*.mp3"))
    
    assert len(wav_files) >= 1, "No WAV files found"
    assert len(mp3_files) >= 1, "No MP3 files found"
    
    # Find the most recent files (should be from this job)
    latest_wav = max(wav_files, key=lambda f: f.stat().st_mtime)
    latest_mp3 = max(mp3_files, key=lambda f: f.stat().st_mtime)
    
    print(f"✓ WAV file: {latest_wav.name} ({latest_wav.stat().st_size:,} bytes)")
    print(f"✓ MP3 file: {latest_mp3.name} ({latest_mp3.stat().st_size:,} bytes)")
    
    # Basic validation: MP3 should be smaller than WAV
    assert latest_mp3.stat().st_size < latest_wav.stat().st_size, \
        "MP3 should be smaller than WAV"
    
    print("=" * 80)
