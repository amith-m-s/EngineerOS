"""Digital twin repository — data access for engineer digital twins."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4

from .base import InMemoryRepository


@dataclass
class TwinRecord:
    """Lightweight storage record for a digital twin snapshot."""

    id: str = field(default_factory=lambda: f"twin_{uuid4().hex[:12]}")
    user_id: str = ""
    title: str = ""
    skill_scores_json: str = "[]"
    debugging_score: int = 0
    architecture_score: int = 0
    reliability_score: int = 0
    leadership_score: int = 0
    system_design_score: int = 0
    memory_count: int = 0
    graph_nodes: int = 0
    vector_embeddings: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TwinRepository(InMemoryRepository[TwinRecord]):
    """In-memory twin repository."""

    def __init__(self) -> None:
        super().__init__(id_field="id")
        self._user_index: dict[str, str] = {}  # user_id → twin_id

    async def create(self, entity: TwinRecord) -> TwinRecord:
        result = await super().create(entity)
        self._user_index[entity.user_id] = entity.id
        return result

    async def find_by_user_id(self, user_id: str) -> TwinRecord | None:
        """Lookup a twin by the owning user_id."""
        twin_id = self._user_index.get(user_id)
        if twin_id is None:
            return None
        return await self.get_by_id(twin_id)

    async def upsert_for_user(self, user_id: str, updates: dict) -> TwinRecord:
        """Create or update twin for a given user."""
        existing = await self.find_by_user_id(user_id)
        if existing:
            updates["updated_at"] = datetime.now(UTC)
            return await self.update(existing.id, updates)  # type: ignore[return-value]
        record = TwinRecord(user_id=user_id, **updates)
        return await self.create(record)


# Singleton
_twin_repo: TwinRepository | None = None


def get_twin_repository() -> TwinRepository:
    """Get the singleton TwinRepository instance."""
    global _twin_repo
    if _twin_repo is None:
        _twin_repo = TwinRepository()
    return _twin_repo
