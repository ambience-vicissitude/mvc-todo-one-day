"""Tests for the users API endpoints."""

from tests.conftest import make_user


def test_duplicate_user_name_conflicts_and_rolls_back(client):
    """Database uniqueness rejects duplicates and the session remains usable afterward."""
    make_user(client, "alice")

    response = client.post("/api/users", json={"name": "alice"})

    assert response.status_code == 409
    assert client.post("/api/users", json={"name": "bob"}).status_code == 201
