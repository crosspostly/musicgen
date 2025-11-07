from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import Settings


def test_health_endpoint_reports_ok(client: TestClient, settings: Settings) -> None:
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == settings.environment
    assert payload["database"]["connected"] is True
    assert payload["database"]["url"] == settings.database_url
    assert payload["storage"]["exists"] is True
    assert payload["modelCache"]["exists"] is True
