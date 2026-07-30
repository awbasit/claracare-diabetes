import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent


class EventDetailService(Protocol):
    """Per-event-type plugin: owns the detail table for one HealthEvent.event_type.

    Registered against health_event_service's dispatch table (see
    register_detail_service) rather than imported here directly, so this
    module never has to know GlucoseLog (or any other detail table) exists.
    """

    async def create_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, detail_data: dict[str, Any]
    ) -> Any: ...

    async def get_detail(self, db: AsyncSession, health_event_id: uuid.UUID) -> Any | None: ...

    async def get_details_for_events(
        self, db: AsyncSession, health_event_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, Any]: ...

    async def update_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, updates: dict[str, Any]
    ) -> Any: ...


_detail_services: dict[EventType, EventDetailService] = {}


def register_detail_service(event_type: EventType, service: EventDetailService) -> None:
    _detail_services[event_type] = service


def _resolve_detail_service(event_type: EventType) -> EventDetailService:
    try:
        return _detail_services[event_type]
    except KeyError as err:
        raise ValueError(
            f"No detail service registered for event type '{event_type.value}'"
        ) from err


async def get_own_event(
    db: AsyncSession, patient_id: uuid.UUID, event_id: uuid.UUID
) -> HealthEvent | None:
    result = await db.execute(
        select(HealthEvent).where(HealthEvent.id == event_id, HealthEvent.patient_id == patient_id)
    )
    return result.scalar_one_or_none()


async def get_own_event_of_type(
    db: AsyncSession, patient_id: uuid.UUID, event_id: uuid.UUID, event_type: EventType
) -> HealthEvent | None:
    """Like get_own_event, but also requires the event to be of the given type.

    Used by each type's router so e.g. a glucose reading's id can't be looked
    up through the meals endpoint — the underlying query doesn't filter by
    type, since get_own_event is shared across all event types.
    """
    event = await get_own_event(db, patient_id, event_id)
    if event is None or event.event_type != event_type:
        return None
    return event


async def get_event_detail(db: AsyncSession, event: HealthEvent) -> Any:
    detail_service = _resolve_detail_service(event.event_type)
    return await detail_service.get_detail(db, event.id)


async def _attach_details(
    db: AsyncSession, events: list[HealthEvent]
) -> list[tuple[HealthEvent, Any]]:
    """Attach each event's detail row, batched by type.

    Each event type has its own detail table, so this can't be one SQL join
    across all of them — but grouping by type and issuing one
    `WHERE health_event_id IN (...)` query per type keeps the query count
    bounded by the number of distinct types in `events` (at most 8), rather
    than growing with len(events) the way a per-event lookup would.
    """
    events_by_type: dict[EventType, list[HealthEvent]] = defaultdict(list)
    for event in events:
        events_by_type[event.event_type].append(event)

    details_by_id: dict[uuid.UUID, Any] = {}
    for event_type, type_events in events_by_type.items():
        detail_service = _resolve_detail_service(event_type)
        event_ids = [event.id for event in type_events]
        details_by_id.update(await detail_service.get_details_for_events(db, event_ids))

    return [(event, details_by_id.get(event.id)) for event in events]


async def create_event(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    event_type: EventType,
    event_timestamp: datetime,
    notes: str | None,
    detail_data: dict[str, Any],
) -> tuple[HealthEvent, Any]:
    # Resolve the detail service before writing anything — an unregistered
    # event_type must not leave a HealthEvent row with no detail attached.
    detail_service = _resolve_detail_service(event_type)

    event = HealthEvent(
        patient_id=patient_id,
        event_type=event_type,
        event_timestamp=event_timestamp,
        notes=notes,
    )
    db.add(event)
    await db.flush()  # assigns event.id without committing yet

    detail = await detail_service.create_detail(db, event.id, detail_data)

    await db.commit()
    await db.refresh(event)
    return event, detail


async def get_events(
    db: AsyncSession,
    patient_id: uuid.UUID,
    *,
    event_types: list[EventType] | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[HealthEvent, Any]]:
    """List events for a patient, optionally scoped to a subset of types.

    event_types=None means "all types" — used by the unified timeline.
    Individual per-type endpoints (glucose, meals, ...) pass a single-item
    list so this one function serves both without a per-type call.
    """
    stmt = select(HealthEvent).where(HealthEvent.patient_id == patient_id)
    if event_types is not None:
        stmt = stmt.where(HealthEvent.event_type.in_(event_types))
    if start is not None:
        stmt = stmt.where(HealthEvent.event_timestamp >= start)
    if end is not None:
        stmt = stmt.where(HealthEvent.event_timestamp <= end)
    stmt = stmt.order_by(HealthEvent.event_timestamp.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    events = list(result.scalars().all())

    return await _attach_details(db, events)


async def update_event(
    db: AsyncSession,
    event: HealthEvent,
    *,
    event_updates: dict[str, Any],
    detail_updates: dict[str, Any],
) -> tuple[HealthEvent, Any]:
    for field, value in event_updates.items():
        setattr(event, field, value)

    detail_service = _resolve_detail_service(event.event_type)
    detail = await detail_service.update_detail(db, event.id, detail_updates)

    await db.commit()
    await db.refresh(event)
    return event, detail


async def delete_event(db: AsyncSession, event: HealthEvent) -> None:
    await db.delete(event)
    await db.commit()
