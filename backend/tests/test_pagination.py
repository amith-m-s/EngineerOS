"""Regression tests for pagination parameter and response validation."""

import pytest
from pydantic import ValidationError

from app.pagination import PaginatedResponse, PaginationParams


def test_pagination_params_defaults_to_first_page() -> None:
    params = PaginationParams()

    assert params.page == 1
    assert params.limit == 20
    assert params.skip == 0


def test_pagination_params_calculates_skip_for_later_pages() -> None:
    assert PaginationParams(page=3, limit=25).skip == 50


@pytest.mark.parametrize(
    "payload",
    [{"page": 0}, {"limit": 0}, {"limit": 101}, {"sort_order": "up"}],
)
def test_pagination_params_rejects_invalid_values(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        PaginationParams(**payload)


def test_paginated_response_calculates_page_flags() -> None:
    response = PaginatedResponse[int].create([11, 12], total=25, page=2, limit=10)

    assert response.pages == 3
    assert response.has_next is True
    assert response.has_prev is True


def test_paginated_response_handles_empty_result_set() -> None:
    response = PaginatedResponse[str].create([], total=0, page=1, limit=10)

    assert response.pages == 0
    assert response.has_next is False
    assert response.has_prev is False


@pytest.mark.parametrize(
    ("total", "page", "limit", "message"),
    [
        (-1, 1, 10, "total must be non-negative"),
        (10, 0, 10, "page must be at least 1"),
        (10, 1, 0, "limit must be at least 1"),
    ],
)
def test_paginated_response_rejects_invalid_values(
    total: int, page: int, limit: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        PaginatedResponse[int].create([], total=total, page=page, limit=limit)
