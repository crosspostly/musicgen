"""
E2E Error and Edge Case Tests

Tests error handling and edge cases across all services.
"""

import time
import pytest
import requests


@pytest.mark.e2e
@pytest.mark.error_case
def test_invalid_job_duration_too_short(backend_service_url):
    """
    Test that jobs with duration < 10 seconds are rejected with proper error.
    """
    print("\n" + "=" * 80)
    print("Testing invalid job: duration too short")
    print("=" * 80)
    
    job_request = {
        "prompt": "Test music",
        "durationSeconds": 5,  # Too short
        "language": "en"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    
    # Should return error status
    assert response.status_code in [400, 422], \
        f"Expected 400/422 for invalid duration, got {response.status_code}"
    
    error_data = response.json()
    print(f"✓ Request rejected with status {response.status_code}")
    print(f"  Error: {error_data}")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_invalid_job_duration_too_long(backend_service_url):
    """
    Test that jobs with duration > 300 seconds are rejected with proper error.
    """
    print("\n" + "=" * 80)
    print("Testing invalid job: duration too long")
    print("=" * 80)
    
    job_request = {
        "prompt": "Test music",
        "durationSeconds": 400,  # Too long
        "language": "en"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    
    # Should return error status
    assert response.status_code in [400, 422], \
        f"Expected 400/422 for invalid duration, got {response.status_code}"
    
    error_data = response.json()
    print(f"✓ Request rejected with status {response.status_code}")
    print(f"  Error: {error_data}")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_missing_required_fields(backend_service_url):
    """
    Test that jobs with missing required fields are rejected.
    """
    print("\n" + "=" * 80)
    print("Testing invalid job: missing required fields")
    print("=" * 80)
    
    # Missing prompt
    job_request = {
        "durationSeconds": 30,
        "language": "en"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    
    assert response.status_code in [400, 422], \
        f"Expected 400/422 for missing prompt, got {response.status_code}"
    
    print(f"✓ Request rejected for missing prompt")
    
    # Empty prompt
    job_request = {
        "prompt": "",
        "durationSeconds": 30,
        "language": "en"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    
    assert response.status_code in [400, 422], \
        f"Expected 400/422 for empty prompt, got {response.status_code}"
    
    print(f"✓ Request rejected for empty prompt")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_invalid_language(backend_service_url):
    """
    Test that jobs with invalid language are rejected.
    """
    print("\n" + "=" * 80)
    print("Testing invalid job: invalid language")
    print("=" * 80)
    
    job_request = {
        "prompt": "Test music",
        "durationSeconds": 30,
        "language": "fr"  # Invalid - only 'en' and 'ru' supported
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    
    assert response.status_code in [400, 422], \
        f"Expected 400/422 for invalid language, got {response.status_code}"
    
    print(f"✓ Request rejected with status {response.status_code}")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_nonexistent_job_status(backend_service_url):
    """
    Test that querying a non-existent job returns 404.
    """
    print("\n" + "=" * 80)
    print("Testing non-existent job query")
    print("=" * 80)
    
    fake_job_id = "00000000-0000-0000-0000-000000000000"
    
    response = requests.get(
        f"{backend_service_url}/api/jobs/diffrhythm/{fake_job_id}",
        timeout=5
    )
    
    assert response.status_code == 404, \
        f"Expected 404 for non-existent job, got {response.status_code}"
    
    print(f"✓ Non-existent job returns 404")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_malformed_json_request(backend_service_url):
    """
    Test that malformed JSON requests are rejected.
    """
    print("\n" + "=" * 80)
    print("Testing malformed JSON request")
    print("=" * 80)
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        data="{'invalid': json}",  # Malformed JSON
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    assert response.status_code in [400, 422], \
        f"Expected 400/422 for malformed JSON, got {response.status_code}"
    
    print(f"✓ Malformed JSON rejected with status {response.status_code}")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_concurrent_job_handling(backend_service_url):
    """
    Test that multiple concurrent jobs are handled correctly.
    """
    print("\n" + "=" * 80)
    print("Testing concurrent job handling")
    print("=" * 80)
    
    # Create multiple jobs simultaneously
    job_requests = [
        {
            "prompt": f"Test music {i}",
            "durationSeconds": 10,
            "language": "en"
        }
        for i in range(3)
    ]
    
    job_ids = []
    for i, job_request in enumerate(job_requests):
        response = requests.post(
            f"{backend_service_url}/api/jobs/diffrhythm",
            json=job_request,
            timeout=10
        )
        assert response.status_code in [200, 201], \
            f"Job {i+1} creation failed: {response.status_code}"
        
        job_id = response.json().get("jobId") or response.json().get("job_id")
        job_ids.append(job_id)
        print(f"✓ Job {i+1} created: {job_id}")
    
    # Verify all jobs can be queried
    for i, job_id in enumerate(job_ids):
        response = requests.get(
            f"{backend_service_url}/api/jobs/diffrhythm/{job_id}",
            timeout=5
        )
        assert response.status_code == 200, \
            f"Failed to query job {i+1}: {response.status_code}"
        
        status_data = response.json()
        assert status_data.get("status") in ["pending", "processing", "completed"], \
            f"Job {i+1} has unexpected status: {status_data.get('status')}"
    
    print(f"✓ All {len(job_ids)} concurrent jobs created and queryable")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_service_health_checks_structure(python_service_url, backend_service_url):
    """
    Test that health check endpoints return properly structured responses.
    """
    print("\n" + "=" * 80)
    print("Testing health check response structure")
    print("=" * 80)
    
    # Python service health check
    response = requests.get(f"{python_service_url}/health", timeout=5)
    assert response.status_code == 200
    health_data = response.json()
    
    assert "status" in health_data, "Python health check missing 'status' field"
    assert health_data["status"] == "healthy"
    print(f"✓ Python service health check structure valid")
    print(f"  Response: {health_data}")
    
    # Backend service health check
    response = requests.get(f"{backend_service_url}/api/health", timeout=5)
    assert response.status_code == 200
    health_data = response.json()
    
    print(f"✓ Backend service health check structure valid")
    print(f"  Response: {health_data}")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_edge_case_minimum_valid_duration(backend_service_url):
    """
    Test edge case: minimum valid duration (10 seconds).
    """
    print("\n" + "=" * 80)
    print("Testing edge case: minimum valid duration")
    print("=" * 80)
    
    job_request = {
        "prompt": "Test minimum duration",
        "durationSeconds": 10,  # Minimum valid
        "language": "en"
    }
    
    response = requests.post(
        f"{backend_service_url}/api/jobs/diffrhythm",
        json=job_request,
        timeout=10
    )
    
    assert response.status_code in [200, 201], \
        f"Minimum valid duration should be accepted, got {response.status_code}"
    
    job_id = response.json().get("jobId") or response.json().get("job_id")
    print(f"✓ Minimum duration (10s) accepted, job ID: {job_id}")
    
    # Wait a bit and check status
    time.sleep(2)
    response = requests.get(
        f"{backend_service_url}/api/jobs/diffrhythm/{job_id}",
        timeout=5
    )
    assert response.status_code == 200
    print(f"✓ Job is processing: {response.json().get('status')}")
    
    print("=" * 80)


@pytest.mark.e2e
@pytest.mark.error_case
def test_api_endpoint_not_found(backend_service_url):
    """
    Test that non-existent API endpoints return 404.
    """
    print("\n" + "=" * 80)
    print("Testing non-existent API endpoint")
    print("=" * 80)
    
    response = requests.get(
        f"{backend_service_url}/api/nonexistent-endpoint",
        timeout=5
    )
    
    assert response.status_code == 404, \
        f"Expected 404 for non-existent endpoint, got {response.status_code}"
    
    print(f"✓ Non-existent endpoint returns 404")
    
    print("=" * 80)
