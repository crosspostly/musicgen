"""
E2E Smoke Test

Quick smoke test to verify basic E2E infrastructure is working.
"""

import pytest
import requests


@pytest.mark.e2e
def test_smoke_services_start(python_service_url, backend_service_url, frontend_service_url):
    """
    Smoke test: Verify all services start and respond to health checks.
    """
    print("\n" + "=" * 80)
    print("Smoke Test: Service Startup")
    print("=" * 80)
    
    # Check Python service
    response = requests.get(f"{python_service_url}/health", timeout=5)
    assert response.status_code == 200, f"Python service health check failed: {response.status_code}"
    print(f"✓ Python service (port 8000): {response.json()}")
    
    # Check Backend service
    response = requests.get(f"{backend_service_url}/api/health", timeout=5)
    assert response.status_code == 200, f"Backend service health check failed: {response.status_code}"
    print(f"✓ Backend service (port 3001): {response.json()}")
    
    # Check Frontend service
    response = requests.get(frontend_service_url, timeout=5)
    assert response.status_code == 200, f"Frontend service failed: {response.status_code}"
    print(f"✓ Frontend service (port 3000): OK")
    
    print("=" * 80)
    print("✓ Smoke test passed - all services responding")
    print("=" * 80)
