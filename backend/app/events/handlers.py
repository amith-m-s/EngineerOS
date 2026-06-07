"""Event handlers — side-effects triggered by domain events.

These handlers run asynchronously after business operations complete.
They perform cross-cutting concerns like logging, metrics, and cache
invalidation without polluting the core domain logic.
"""

from __future__ import annotations

import logging

from ..domain.events import (
    DomainEvent,
    IncidentResolved,
    MemoryRecorded,
    SimulationCompleted,
    SkillRecalculated,
    TwinUpdated,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)
from ..observability import record_login, record_memory, record_simulation

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Handler implementations
# ---------------------------------------------------------------------------

async def on_twin_updated(event: DomainEvent) -> None:
    """Log twin update and invalidate any cached twin data."""
    assert isinstance(event, TwinUpdated)
    logger.info(
        "Twin updated for user %s — fields: %s",
        event.user_id,
        ", ".join(event.changed_fields) or "all",
    )


async def on_skill_recalculated(event: DomainEvent) -> None:
    """Record skill score change for metrics and audit."""
    assert isinstance(event, SkillRecalculated)
    delta = event.new_score - event.old_score
    direction = "↑" if delta > 0 else "↓" if delta < 0 else "="
    logger.info(
        "Skill recalculated: user=%s domain=%s %d→%d (%s%d)",
        event.user_id,
        event.domain,
        event.old_score,
        event.new_score,
        direction,
        abs(delta),
    )


async def on_incident_resolved(event: DomainEvent) -> None:
    """Log incident resolution and record MTTR metric."""
    assert isinstance(event, IncidentResolved)
    logger.info(
        "Incident %s resolved by %s in %.1fs",
        event.incident_id,
        event.resolver_user_id,
        event.resolution_seconds,
    )


async def on_memory_recorded(event: DomainEvent) -> None:
    """Record memory creation in Prometheus."""
    assert isinstance(event, MemoryRecorded)
    record_memory(event.kind)
    logger.info(
        "Memory recorded: user=%s kind=%s strength=%.2f",
        event.user_id,
        event.kind,
        event.signal_strength,
    )


async def on_simulation_completed(event: DomainEvent) -> None:
    """Record simulation completion in Prometheus."""
    assert isinstance(event, SimulationCompleted)
    record_simulation(event.difficulty)
    logger.info(
        "Simulation completed: id=%s user=%s scenario=%s score=%.1f",
        event.simulation_id,
        event.user_id,
        event.scenario,
        event.score,
    )


async def on_user_registered(event: DomainEvent) -> None:
    """Log new user registration."""
    assert isinstance(event, UserRegistered)
    logger.info("New user registered: user_id=%s email=%s", event.user_id, event.email)


async def on_user_logged_in(event: DomainEvent) -> None:
    """Record successful login metric."""
    assert isinstance(event, UserLoggedIn)
    record_login("success")
    logger.info("User logged in: user_id=%s", event.user_id)


async def on_user_logged_out(event: DomainEvent) -> None:
    """Log user logout."""
    assert isinstance(event, UserLoggedOut)
    logger.info("User logged out: user_id=%s", event.user_id)


# ---------------------------------------------------------------------------
# Registration helper
# ---------------------------------------------------------------------------

def register_handlers(bus) -> None:
    """Wire all handlers to the event bus."""
    bus.subscribe(TwinUpdated, on_twin_updated)
    bus.subscribe(SkillRecalculated, on_skill_recalculated)
    bus.subscribe(IncidentResolved, on_incident_resolved)
    bus.subscribe(MemoryRecorded, on_memory_recorded)
    bus.subscribe(SimulationCompleted, on_simulation_completed)
    bus.subscribe(UserRegistered, on_user_registered)
    bus.subscribe(UserLoggedIn, on_user_logged_in)
    bus.subscribe(UserLoggedOut, on_user_logged_out)
    logger.info("All domain event handlers registered")
