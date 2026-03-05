"""Basic integration tests for public API contract."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_ping_smoke(client: TestClient) -> None:
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.integration
def test_healthz_smoke(client: TestClient) -> None:
    resp = client.get("/api/v1/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["dev_code"] == "HEALTH_OK"
    assert body["metadata"]["request_id"]
