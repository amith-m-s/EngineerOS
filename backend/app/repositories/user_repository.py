"""User repository — data access for engineer profiles / user accounts.

Pre-seeded with a demo user so the application works out of the box.
"""

from __future__ import annotations

from datetime import datetime, UTC

from ..domain.entities import EngineerProfile
from ..domain.exceptions import DuplicateEntity, EntityNotFound
from .base import InMemoryRepository


class UserRepository(InMemoryRepository[EngineerProfile]):
    """In-memory user repository with email-based lookup."""

    def __init__(self) -> None:
        super().__init__(id_field="user_id")
        self._email_index: dict[str, str] = {}  # email → user_id

    # ------------------------------------------------------------------
    # Seed demo user on first instantiation
    # ------------------------------------------------------------------
    async def seed_demo_user(self) -> None:
        """Pre-populate with a demo user for development."""
        from ..auth import hash_password

        demo = EngineerProfile(
            id="eng_demo_user",
            user_id="demo_user",
            email="demo@engineeros.io",
            full_name="Demo Engineer",
            title="Senior Backend Engineer",
            roles=["engineer"],
            is_active=True,
            is_verified=True,
            password_hash=hash_password("demo1234"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await self.create(demo)

    # ------------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------------
    async def create(self, entity: EngineerProfile) -> EngineerProfile:
        """Create user, enforcing email uniqueness."""
        if entity.email in self._email_index:
            raise DuplicateEntity("User", "email", entity.email)
        result = await super().create(entity)
        self._email_index[entity.email] = entity.user_id
        return result

    async def delete(self, entity_id: str) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity:
            self._email_index.pop(entity.email, None)
        return await super().delete(entity_id)

    # ------------------------------------------------------------------
    # Custom queries
    # ------------------------------------------------------------------
    async def find_by_email(self, email: str) -> EngineerProfile | None:
        """Lookup a user by email address."""
        user_id = self._email_index.get(email)
        if user_id is None:
            return None
        return await self.get_by_id(user_id)

    async def find_by_id(self, user_id: str) -> EngineerProfile | None:
        """Alias for get_by_id with the user_id key."""
        return await self.get_by_id(user_id)

    async def update_password(self, user_id: str, new_hash: str) -> EngineerProfile | None:
        """Update a user's password hash."""
        return await self.update(user_id, {
            "password_hash": new_hash,
            "updated_at": datetime.now(UTC),
        })


# ---------------------------------------------------------------------------
# Singleton instance (replaced by DI container in production)
# ---------------------------------------------------------------------------
_user_repo: UserRepository | None = None


def get_user_repository() -> UserRepository:
    """Get the singleton UserRepository instance."""
    global _user_repo
    if _user_repo is None:
        _user_repo = UserRepository()
    return _user_repo
