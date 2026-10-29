"""Tests for the health check API endpoints."""


def test_health_endpoints(client):
    """Test the health check endpoints."""

    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/health/ready").json() == {"status": "ready"}
