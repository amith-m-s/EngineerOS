"""Regression tests for correlation ID input validation."""

from uuid import UUID

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.middleware.correlation_id import (
    HEADER_NAME,
    MAX_CORRELATION_ID_LENGTH,
    CorrelationIdMiddleware,
    get_correlation_id,
)


def _request_with_correlation_id(value: bytes | None = None) -> Request:
    headers = [] if value is None else [(b"x-correlation-id", value)]
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": headers,
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
        }
    )


def _middleware() -> CorrelationIdMiddleware:
    return CorrelationIdMiddleware(app=lambda scope, receive, send: None)


@pytest.mark.asyncio
async def test_valid_client_correlation_id_is_preserved() -> None:
    correlation_id = "trace:service/123-ABC"
    observed: list[str] = []

    async def call_next(_request: Request) -> Response:
        observed.append(get_correlation_id())
        return Response("ok")

    response = await _middleware().dispatch(
        _request_with_correlation_id(correlation_id.encode("ascii")),
        call_next,
    )

    assert observed == [correlation_id]
    assert response.headers[HEADER_NAME] == correlation_id
    assert get_correlation_id() == ""


@pytest.mark.asyncio
async def test_missing_correlation_id_is_generated() -> None:
    observed: list[str] = []

    async def call_next(_request: Request) -> Response:
        observed.append(get_correlation_id())
        return Response("ok")

    response = await _middleware().dispatch(_request_with_correlation_id(), call_next)

    generated_id = response.headers[HEADER_NAME]
    assert str(UUID(generated_id)) == generated_id
    assert observed == [generated_id]
    assert get_correlation_id() == ""


@pytest.mark.asyncio
async def test_maximum_length_correlation_id_is_accepted() -> None:
    correlation_id = "a" * MAX_CORRELATION_ID_LENGTH

    async def call_next(_request: Request) -> Response:
        return Response("ok")

    response = await _middleware().dispatch(
        _request_with_correlation_id(correlation_id.encode("ascii")),
        call_next,
    )

    assert response.headers[HEADER_NAME] == correlation_id


@pytest.mark.parametrize(
    "value",
    [
        b"a" * (MAX_CORRELATION_ID_LENGTH + 1),
        b"contains whitespace",
        b"contains\x00control",
        b"contains\x7fdelete",
        b"contains\xffnon-ascii",
    ],
)
@pytest.mark.asyncio
async def test_malformed_correlation_id_is_replaced(value: bytes) -> None:
    async def call_next(_request: Request) -> Response:
        return Response("ok")

    response = await _middleware().dispatch(
        _request_with_correlation_id(value),
        call_next,
    )

    generated_id = response.headers[HEADER_NAME]
    assert str(UUID(generated_id)) == generated_id
