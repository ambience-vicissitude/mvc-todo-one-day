"""Test fixtures for the FastAPI app."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import create_app
from app.models import Base


@pytest.fixture
def client():
    """Create a test client for the FastAPI app.

    Returns:
        TestClient: The test client instance.
    """

    # In-memory SQLite keeps tests fast and dependency-free; the compose integration test
    # covers real Postgres. TRIMMED: no Postgres-specific tests (e.g. via testcontainers).
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


def make_user(client: TestClient, name: str) -> dict[str, str]:
    """Create a user via the API and return the authentication headers.

    Args:
        client (TestClient): The test client instance.
        name (str): The name of the user to create.

    Returns:
        dict[str, str]: The headers containing the user ID.
    """
    response = client.post("/api/users", json={"name": name})
    assert response.status_code == 201
    return {"X-User-Id": str(response.json()["id"])}
