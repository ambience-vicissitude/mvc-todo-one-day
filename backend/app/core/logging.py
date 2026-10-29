"""Logging configuration and request logging middleware."""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger("app.http")


def configure_logging(level: str) -> None:
    """Configure logging for the application."""

    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )


async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Log incoming HTTP requests and their response times."""

    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    # Probe traffic would drown real requests at INFO.
    level = logging.DEBUG if request.url.path.startswith("/api/health") else logging.INFO
    logger.log(
        level,
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response
