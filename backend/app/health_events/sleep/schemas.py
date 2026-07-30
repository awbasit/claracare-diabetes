import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel

from app.health_events.models.enums import EventSource, SleepQuality
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.sleep_log import SleepLog


class SleepLogCreate(BaseModel):
    event_timestamp: datetime
    bedtime: datetime
    wake_time: datetime
    hours_slept: float
    quality: SleepQuality
    night_awakenings: int = 0
    notes: str | None = None


class SleepLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    bedtime: datetime | None = None
    wake_time: datetime | None = None
    hours_slept: float | None = None
    quality: SleepQuality | None = None
    night_awakenings: int | None = None
    notes: str | None = None


class SleepLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    bedtime: datetime
    wake_time: datetime
    hours_slept: float
    quality: SleepQuality
    night_awakenings: int

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: SleepLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            bedtime=detail.bedtime,
            wake_time=detail.wake_time,
            hours_slept=detail.hours_slept,
            quality=detail.quality,
            night_awakenings=detail.night_awakenings,
        )
