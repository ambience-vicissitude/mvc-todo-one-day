"""Health check endpoints.

For K8s: Liveness skips the DB; readiness handles database availability.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.dependencies import DbSession

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def liveness():
    """Process is up."""

    return {"status": "ok"}


@router.get("/ready")
def readiness(db: DbSession):
    """Ready to take traffic: the database answers."""

    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unavailable") from exc
    return {"status": "ready"}
