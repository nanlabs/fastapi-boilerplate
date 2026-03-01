"""Tests for RequestIDMiddleware."""

import re

from fastapi.testclient import TestClient


class TestRequestIDMiddleware:
    def test_response_has_request_id_header(self, client: TestClient) -> None:
        response = client.get("/ping")
        assert "X-Request-ID" in response.headers

    def test_request_id_is_uuid(self, client: TestClient) -> None:
        response = client.get("/ping")
        request_id = response.headers["X-Request-ID"]
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        assert re.match(uuid_pattern, request_id, re.IGNORECASE)

    def test_client_provided_request_id_is_reused(self, client: TestClient) -> None:
        custom_id = "my-custom-request-id"
        response = client.get("/ping", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id

    def test_different_requests_have_different_ids(self, client: TestClient) -> None:
        first = client.get("/ping")
        second = client.get("/ping")
        assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]
