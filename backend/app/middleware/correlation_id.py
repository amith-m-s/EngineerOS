"""Correlation ID middleware.

Generates or propagates an ``X-Correlation-ID`` header on every request
and stores it in a ``contextvars.ContextVar`` so any code in the call
stack can access the current correlation ID without passing it around.
"""

from __future__ import annotations

import contextvars
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ContextVar available to any code running within the request lifecycle
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)

HEADER_NAME = "X-Correlation-ID"
MAX_CORRELATION_ID_LENGTH = 128


def get_correlation_id() -> str:
    """Get the current request's correlation ID (empty string if outside request)."""
    return correlation_id_var.get()


def _validated_correlation_id(value: str | None) -> str:
    """Accept bounded visible-ASCII IDs; replace malformed values with a UUID."""
    if value and len(value) <= MAX_CORRELATION_ID_LENGTH and all(
        0x21 <= ord(character) <= 0x7E for character in value
    ):
        return value

    return str(uuid4())


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that manages correlation IDs for request tracing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Do not reflect unbounded or non-printable client input into responses/logs.
        cid = _validated_correlation_id(request.headers.get(HEADER_NAME))
        token = correlation_id_var.set(cid)

        try:
            response: Response = await call_next(request)
            response.headers[HEADER_NAME] = cid
            return response
        finally:
            correlation_id_var.reset(token)
