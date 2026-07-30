import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel

from app.health_events.models.enums import EventSource
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.medication_log import MedicationLog


class MedicationLogCreate(BaseModel):
    event_timestamp: datetime
    medication_id: uuid.UUID
    scheduled_time: datetime | None = None
    actual_time: datetime
    taken: bool
    missed_reason: str | None = None
    notes: str | None = None


class MedicationLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    medication_id: uuid.UUID | None = None
    scheduled_time: datetime | None = None
    actual_time: datetime | None = None
    taken: bool | None = None
    missed_reason: str | None = None
    notes: str | None = None


class MedicationLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    medication_id: uuid.UUID
    scheduled_time: datetime | None
    actual_time: datetime
    taken: bool
    missed_reason: str | None

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: MedicationLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            medication_id=detail.medication_id,
            scheduled_time=detail.scheduled_time,
            actual_time=detail.actual_time,
            taken=detail.taken,
            missed_reason=detail.missed_reason,
        )
