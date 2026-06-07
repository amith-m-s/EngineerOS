"""Memory repository — data access for engineer memory entries."""

from __future__ import annotations

from datetime import datetime, UTC

from ..domain.entities import MemoryEntry
from .base import InMemoryRepository


class MemoryRepository(InMemoryRepository[MemoryEntry]):
    """In-memory memory repository with user-scoped queries."""

    def __init__(self) -> None:
        super().__init__(id_field="id")
        # Secondary index: user_id → list of memory IDs
        self._user_index: dict[str, list[str]] = {}

    async def create(self, entity: MemoryEntry) -> MemoryEntry:
        result = await super().create(entity)
        self._user_index.setdefault(entity.user_id, []).append(entity.id)
        return result

    async def delete(self, entity_id: str) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity and entity.user_id in self._user_index:
            self._user_index[entity.user_id] = [
                mid for mid in self._user_index[entity.user_id] if mid != entity_id
            ]
        return await super().delete(entity_id)

    async def find_by_user_id(
        self,
        user_id: str,
        *,
        kind: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MemoryEntry]:
        """Get memories for a user, optionally filtered by kind."""
        memory_ids = self._user_index.get(user_id, [])
        results: list[MemoryEntry] = []
        for mid in memory_ids:
            entry = await self.get_by_id(mid)
            if entry is None:
                continue
            if kind and entry.kind != kind:
                continue
            results.append(entry)

        # Sort by created_at descending (most recent first)
        results.sort(key=lambda m: m.created_at, reverse=True)
        return results[offset: offset + limit]

    async def count_for_user(self, user_id: str) -> int:
        """Count memories for a given user."""
        return len(self._user_index.get(user_id, []))


# Singleton
_memory_repo: MemoryRepository | None = None


def get_memory_repository() -> MemoryRepository:
    """Get the singleton MemoryRepository instance."""
    global _memory_repo
    if _memory_repo is None:
        _memory_repo = MemoryRepository()
    return _memory_repo
