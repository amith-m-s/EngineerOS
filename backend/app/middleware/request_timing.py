"""Request timing middleware.

Records request duration and logs slow requests (>500 ms).
Feeds timing data into the Prometheus metrics system.
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

SLOW_REQUEST_THRESHOLD_SECONDS = 0.5


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware that measures and records request duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        response: Response = await call_next(request)

        duration = time.perf_counter() - start
        response.headers["X-Response-Time-Ms"] = f"{duration * 1000:.1f}"

        # Log slow requests
        if duration > SLOW_REQUEST_THRESHOLD_SECONDS:
            logger.warning(
                "Slow request: %s %s took %.3fs",
                request.method,
                request.url.path,
                duration,
            )

        # Feed Prometheus metrics (lazy import to avoid circular deps)
        try:
            from ..observability import record_request

            record_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration,
            )
        except Exception:
            pass  # Metrics are best-effort; never break the request

        return response
