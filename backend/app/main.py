"""Main application entry point for the Task Manager API."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers import health, tasks, users
from app.core.config import get_settings
from app.core.exceptions import BusinessRuleError, ConflictError, DomainError, NotFoundError
from app.core.logging import configure_logging, log_requests

logger = logging.getLogger("app")

# Domain error -> HTTP status. Domain errors are mapped to appropriate HTTP status codes here.
_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: 404,
    ConflictError: 409,
    BusinessRuleError: 422,
}


async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
    """Handle domain errors and return appropriate HTTP response."""
    logger.error("Domain error occurred: %s", exc.message)
    return JSONResponse({"detail": exc.message}, status_code=_STATUS_BY_ERROR[type(exc)])


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    # Get application settings and configure logging
    settings = get_settings()
    configure_logging(settings.log_level)

    # Create FastAPI application instance
    app = FastAPI(
        title="Task Manager API",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    # Add middleware for logging requests
    app.middleware("http")(log_requests)
    for error_type in _STATUS_BY_ERROR:
        app.add_exception_handler(error_type, _handle_domain_error)  # pyright: ignore[reportArgumentType]

    # Include API routers
    for router in (health.router, users.router, tasks.router):
        app.include_router(router, prefix="/api")

    logger.info("app started env=%s", settings.app_env)
    return app


app = create_app()
