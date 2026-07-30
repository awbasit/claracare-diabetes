import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel

from app.health_events.models.enums import EventSource
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.vitals_log import VitalsLog


class VitalsLogCreate(BaseModel):
    event_timestamp: datetime
    weight_kg: float | None = None
    blood_pressure_systolic: int | None = None
    blood_pressure_diastolic: int | None = None
    heart_rate: int | None = None
    notes: str | None = None


class VitalsLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    weight_kg: float | None = None
    blood_pressure_systolic: int | None = None
    blood_pressure_diastolic: int | None = None
    heart_rate: int | None = None
    notes: str | None = None


class VitalsLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    weight_kg: float | None
    blood_pressure_systolic: int | None
    blood_pressure_diastolic: int | None
    heart_rate: int | None

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: VitalsLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            weight_kg=detail.weight_kg,
            blood_pressure_systolic=detail.blood_pressure_systolic,
            blood_pressure_diastolic=detail.blood_pressure_diastolic,
            heart_rate=detail.heart_rate,
        )
