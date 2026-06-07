"""Domain events — things that happened in the business domain.

Events are published via the event bus and consumed by handlers for
side-effects (logging, metrics, notifications, cache invalidation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_id: str = field(default_factory=lambda: uuid4().hex)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TwinUpdated(DomainEvent):
    """Fired when an engineer's digital twin is recalculated."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass
class SkillRecalculated(DomainEvent):
    """Fired when a skill score is recalculated."""

    user_id: str = ""
    domain: str = ""
    old_score: int = 0
    new_score: int = 0


@dataclass
class IncidentResolved(DomainEvent):
    """Fired when an incident is resolved."""

    incident_id: str = ""
    resolver_user_id: str = ""
    resolution_seconds: float = 0.0


@dataclass
class MemoryRecorded(DomainEvent):
    """Fired when a new memory entry is created."""

    user_id: str = ""
    memory_id: str = ""
    kind: str = ""
    signal_strength: float = 0.0


@dataclass
class SimulationCompleted(DomainEvent):
    """Fired when a simulation session finishes."""

    simulation_id: str = ""
    user_id: str = ""
    scenario: str = ""
    difficulty: str = ""
    score: float = 0.0


@dataclass
class UserRegistered(DomainEvent):
    """Fired when a new user registers."""

    user_id: str = ""
    email: str = ""


@dataclass
class UserLoggedIn(DomainEvent):
    """Fired when a user logs in."""

    user_id: str = ""
    email: str = ""


@dataclass
class UserLoggedOut(DomainEvent):
    """Fired when a user logs out."""

    user_id: str = ""
