"""Async in-process event bus with type-safe subscribe/publish.

Handlers are registered per event type.  When an event is published,
all matching handlers are invoked concurrently via ``asyncio.gather``.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Awaitable, Type

from ..domain.events import DomainEvent

logger = logging.getLogger(__name__)

# Type alias for an async event handler
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """Simple async event bus for domain events."""

    def __init__(self) -> None:
        self._handlers: dict[Type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed %s to %s", handler.__name__, event_type.__name__)

    def unsubscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Remove a handler for a specific event type."""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers.

        Handlers run concurrently.  Failures in one handler don't prevent
        others from executing.
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug("No handlers for %s", event_type.__name__)
            return

        logger.info(
            "Publishing %s (id=%s) to %d handler(s)",
            event_type.__name__,
            event.event_id,
            len(handlers),
        )

        results = await asyncio.gather(
            *(self._safe_call(handler, event) for handler in handlers),
            return_exceptions=True,
        )

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "Handler %s failed for %s: %s",
                    handlers[i].__name__,
                    event_type.__name__,
                    result,
                    exc_info=result,
                )

    @staticmethod
    async def _safe_call(handler: EventHandler, event: DomainEvent) -> None:
        """Call a handler with error isolation."""
        await handler(event)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

event_bus = EventBus()
