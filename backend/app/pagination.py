"""Pagination utilities for list endpoints."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")

    @property
    def skip(self) -> int:
        """Calculate skip value for database queries."""
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format."""

    items: list[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        limit: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        pages = (total + limit - 1) // limit  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


class CursorPaginationParams(BaseModel):
    """Cursor-based pagination parameters."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response."""

    items: list[T] = Field(description="List of items")
    next_cursor: str | None = Field(description="Cursor for next page")
    has_more: bool = Field(description="Whether there are more items")
    limit: int = Field(description="Items per page")
