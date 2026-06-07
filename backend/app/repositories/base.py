"""Abstract base repository with generic CRUD interface.

Provides a contract that all repositories must implement, plus an
in-memory implementation for development/testing without a real database.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository defining the CRUD contract."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        """Retrieve an entity by its primary identifier."""
        ...

    @abstractmethod
    async def get_all(self, *, limit: int = 100, offset: int = 0) -> list[T]:
        """Retrieve a paginated list of entities."""
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Persist a new entity and return it."""
        ...

    @abstractmethod
    async def update(self, entity_id: str, updates: dict[str, Any]) -> T | None:
        """Apply partial updates to an existing entity."""
        ...

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity by id.  Returns True if it existed."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Return total number of entities."""
        ...


class InMemoryRepository(BaseRepository[T]):
    """Thread-safe in-memory repository for development and testing.

    Stores entities in a plain dict keyed by ``id_field``.
    All returned objects are deep-copied to prevent accidental mutation.
    """

    def __init__(self, *, id_field: str = "id"):
        self._store: dict[str, T] = {}
        self._id_field = id_field

    def _get_id(self, entity: T) -> str:
        """Extract the id value from an entity (works with dataclasses and dicts)."""
        if isinstance(entity, dict):
            return entity[self._id_field]
        return getattr(entity, self._id_field)

    async def get_by_id(self, entity_id: str) -> T | None:
        entity = self._store.get(entity_id)
        return copy.deepcopy(entity) if entity else None

    async def get_all(self, *, limit: int = 100, offset: int = 0) -> list[T]:
        items = list(self._store.values())
        return [copy.deepcopy(item) for item in items[offset: offset + limit]]

    async def create(self, entity: T) -> T:
        entity_id = self._get_id(entity)
        self._store[entity_id] = copy.deepcopy(entity)
        return copy.deepcopy(entity)

    async def update(self, entity_id: str, updates: dict[str, Any]) -> T | None:
        entity = self._store.get(entity_id)
        if entity is None:
            return None

        if isinstance(entity, dict):
            entity.update(updates)
        else:
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

        self._store[entity_id] = entity
        return copy.deepcopy(entity)

    async def delete(self, entity_id: str) -> bool:
        return self._store.pop(entity_id, None) is not None

    async def count(self) -> int:
        return len(self._store)

    async def find_by(self, field: str, value: Any) -> T | None:
        """Find the first entity where *field* equals *value*."""
        for entity in self._store.values():
            if isinstance(entity, dict):
                if entity.get(field) == value:
                    return copy.deepcopy(entity)
            elif getattr(entity, field, None) == value:
                return copy.deepcopy(entity)
        return None
