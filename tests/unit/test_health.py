"""Tests for health endpoints."""

from fastapi.testclient import TestClient


class TestHealthCheck:
    def test_healthz_returns_envelope(self, client: TestClient) -> None:
        response = client.get("/api/v1/healthz")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["dev_code"] == "HEALTH_OK"
        assert body["data"]["status"] == "healthy"
        assert "request_id" in body["metadata"]

    def test_ping_returns_simple_ok(self, client: TestClient) -> None:
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
