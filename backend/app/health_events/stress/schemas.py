import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field

from app.health_events.models.enums import EventSource, Mood
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.stress_log import StressLog


class StressLogCreate(BaseModel):
    event_timestamp: datetime
    stress_level: int = Field(ge=1, le=10)
    mood: Mood
    energy_level: int | None = Field(default=None, ge=1, le=10)
    notes: str | None = None


class StressLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    stress_level: int | None = Field(default=None, ge=1, le=10)
    mood: Mood | None = None
    energy_level: int | None = Field(default=None, ge=1, le=10)
    notes: str | None = None


class StressLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    stress_level: int
    mood: Mood
    energy_level: int | None

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: StressLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            stress_level=detail.stress_level,
            mood=detail.mood,
            energy_level=detail.energy_level,
        )
