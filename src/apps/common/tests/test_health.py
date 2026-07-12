"""Tests for the health-check endpoint."""
import datetime

import pytest


@pytest.mark.django_db
def test_health_ok(api_client):
    resp = api_client.get("/health/")

    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert "timestamp" in data
    assert datetime.datetime.fromisoformat(data["timestamp"])