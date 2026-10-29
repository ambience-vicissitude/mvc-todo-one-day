"""The domain events for the application.

TRIM: Domain-event seam: the extension point for a message queue (MQ).

Services publish events through the EventPublisher port and never know what is behind it.
Today the adapter just logs. To add an MQ (RabbitMQ, Redis Streams, SQS, Kafka):

1. Write an adapter implementing `EventPublisher.publish` that serializes the event to the broker.
2. Return it from `get_event_publisher` in app/dependencies.py. No service code changes
   (open/closed, dependency inversion).
3. Run consumers as separate worker processes/containers.

What it enables, and why:
- Due-date reminders and status-change notifications: slow or optional work runs off the request
  path, so API latency stays flat and a failing email provider cannot fail a task update.
- Audit trail / analytics: consumers subscribe independently without touching task code.
- Spike buffering and retries: the queue absorbs bursts; consumers retry with backoff.

Trade-offs: another system to operate, eventual consistency, consumers must be idempotent, and
publishing alongside the DB commit needs the transactional-outbox pattern to avoid lost events.
Not built here (YAGNI), but this seam keeps the door open.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

logger = logging.getLogger("app.events")


@dataclass(frozen=True)
class DomainEvent:
    """A domain event with a name and payload.

    Attributes:
        name (str): The name of the event.
        payload (dict[str, Any]): The event payload.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventPublisher(Protocol):
    """The interface for publishing domain events."""

    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event.

        Args:
            event (DomainEvent): The event to publish.
        """


class LoggingEventPublisher:
    """An event publisher that logs events."""

    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event by logging it.

        Args:
            event (DomainEvent): The event to publish.
        """
        logger.info("event %s %s", event.name, event.payload)
