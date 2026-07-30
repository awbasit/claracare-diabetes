import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel

from app.health_events.models.enums import EventSource, SymptomSeverity, SymptomType
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.symptom_log import SymptomLog


class SymptomLogCreate(BaseModel):
    event_timestamp: datetime
    symptom_type: SymptomType
    severity: SymptomSeverity
    duration_notes: str | None = None
    notes: str | None = None


class SymptomLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    symptom_type: SymptomType | None = None
    severity: SymptomSeverity | None = None
    duration_notes: str | None = None
    notes: str | None = None


class SymptomLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    symptom_type: SymptomType
    severity: SymptomSeverity
    duration_notes: str | None

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: SymptomLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            symptom_type=detail.symptom_type,
            severity=detail.severity,
            duration_notes=detail.duration_notes,
        )
