"""Unit tests for repository data access layers."""

import pytest
from datetime import UTC, datetime

from app.repositories.user_repository import get_user_repository
from app.repositories.twin_repository import get_twin_repository, TwinRecord
from app.repositories.memory_repository import get_memory_repository
from app.domain.entities import EngineerProfile, MemoryEntry
from app.domain.exceptions import DuplicateEntity


@pytest.mark.asyncio
async def test_user_repository_crud():
    """Test CRUD operations on UserRepository."""
    repo = get_user_repository()
    # Reset repository state for test isolation
    repo._store.clear()
    repo._email_index.clear()

    # Test create
    user = EngineerProfile(
        id="user_1",
        user_id="user_1",
        email="test_repo@engineeros.io",
        full_name="Test User",
        title="Software Engineer",
        roles=["engineer"],
        is_active=True,
        is_verified=True,
        password_hash="hash",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )

    created = await repo.create(user)
    assert created.user_id == "user_1"
    assert created.email == "test_repo@engineeros.io"

    # Test duplicate email constraint
    with pytest.raises(DuplicateEntity):
        await repo.create(user)

    # Test find_by_email
    found = await repo.find_by_email("test_repo@engineeros.io")
    assert found is not None
    assert found.user_id == "user_1"

    # Test find_by_id
    found_id = await repo.find_by_id("user_1")
    assert found_id is not None
    assert found_id.email == "test_repo@engineeros.io"

    # Test update password
    updated = await repo.update_password("user_1", "new_hash")
    assert updated is not None
    assert updated.password_hash == "new_hash"

    # Test delete
    deleted = await repo.delete("user_1")
    assert deleted is True
    assert await repo.find_by_email("test_repo@engineeros.io") is None


@pytest.mark.asyncio
async def test_twin_repository_crud():
    """Test CRUD operations on TwinRepository."""
    repo = get_twin_repository()
    # Reset repository state
    repo._store.clear()
    repo._user_index.clear()

    twin = TwinRecord(
        user_id="user_2",
        title="Systems Architect",
        debugging_score=95,
        architecture_score=90
    )

    created = await repo.create(twin)
    assert created.user_id == "user_2"
    assert created.debugging_score == 95

    # Test upsert
    updated = await repo.upsert_for_user("user_2", {"debugging_score": 98})
    assert updated.debugging_score == 98

    # Test find_by_user_id
    found = await repo.find_by_user_id("user_2")
    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
async def test_memory_repository_crud():
    """Test CRUD operations on MemoryRepository."""
    repo = get_memory_repository()
    # Reset repository state
    repo._store.clear()
    repo._user_index.clear()

    memory = MemoryEntry(
        id="mem_1",
        user_id="user_3",
        kind="decision",
        summary="Chose SQLite in dev",
        signal_strength=0.9,
        created_at=datetime.now(UTC)
    )

    created = await repo.create(memory)
    assert created.id == "mem_1"

    # Test find_by_user_id
    memories = await repo.find_by_user_id("user_3")
    assert len(memories) == 1
    assert memories[0].summary == "Chose SQLite in dev"

    # Test count
    count = await repo.count_for_user("user_3")
    assert count == 1

    # Test delete
    deleted = await repo.delete("mem_1")
    assert deleted is True
    assert await repo.count_for_user("user_3") == 0
