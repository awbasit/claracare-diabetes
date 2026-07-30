import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel, computed_field

from app.health_events.glucose.service import mg_dl_to_mmol_l, mmol_l_to_mg_dl
from app.health_events.models.enums import EventSource, GlucoseReadingType, GlucoseUnit
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.models.health_event import HealthEvent


class GlucoseLogCreate(BaseModel):
    event_timestamp: datetime
    value: float
    unit: GlucoseUnit
    reading_type: GlucoseReadingType
    notes: str | None = None


class GlucoseLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    value: float | None = None
    unit: GlucoseUnit | None = None
    reading_type: GlucoseReadingType | None = None
    notes: str | None = None


class GlucoseLogRead(BaseModel):
    # `id` is the HealthEvent id — the public identifier for "a glucose
    # reading" — not GlucoseLog.id, which is an internal detail-row id.
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    value: float
    unit: GlucoseUnit
    reading_type: GlucoseReadingType
    confidence: float | None
    manually_entered: bool

    @computed_field  # type: ignore[prop-decorator]
    @property
    def value_mg_dl(self) -> float:
        return self.value if self.unit == GlucoseUnit.mg_dl else mmol_l_to_mg_dl(self.value)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def value_mmol_l(self) -> float:
        return self.value if self.unit == GlucoseUnit.mmol_l else mg_dl_to_mmol_l(self.value)

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: GlucoseLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            value=detail.value,
            unit=detail.unit,
            reading_type=detail.reading_type,
            confidence=detail.confidence,
            manually_entered=detail.manually_entered,
        )
