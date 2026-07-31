import uuid
from datetime import datetime

from pydantic import BaseModel


class Observation(BaseModel):
    """Forward-compat type only (design doc §10a) — Sprint 4's Pattern
    Engine will consume this normalized shape instead of reverse-engineering
    eight different HealthEvent detail tables. Nothing in Sprint 3 produces
    or consumes it; declared now so Sprint 4 doesn't need a breaking schema
    change.
    """

    patient_id: uuid.UUID
    source: str  # the event_type this was derived from
    value: float | str
    timestamp: datetime
    confidence: float  # from the relevant DataQuality.consistency/reliability
