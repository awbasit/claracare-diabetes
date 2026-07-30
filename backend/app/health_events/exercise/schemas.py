import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel

from app.health_events.models.enums import EventSource, ExerciseIntensity
from app.health_events.models.exercise_log import ExerciseLog
from app.health_events.models.health_event import HealthEvent


class ExerciseLogCreate(BaseModel):
    event_timestamp: datetime
    exercise_type: str
    duration_minutes: int
    intensity: ExerciseIntensity
    calories_burned: int | None = None
    heart_rate_avg: int | None = None
    notes: str | None = None


class ExerciseLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    exercise_type: str | None = None
    duration_minutes: int | None = None
    intensity: ExerciseIntensity | None = None
    calories_burned: int | None = None
    heart_rate_avg: int | None = None
    notes: str | None = None


class ExerciseLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    exercise_type: str
    duration_minutes: int
    intensity: ExerciseIntensity
    calories_burned: int | None
    heart_rate_avg: int | None

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: ExerciseLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            exercise_type=detail.exercise_type,
            duration_minutes=detail.duration_minutes,
            intensity=detail.intensity,
            calories_burned=detail.calories_burned,
            heart_rate_avg=detail.heart_rate_avg,
        )
