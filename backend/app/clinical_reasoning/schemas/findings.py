import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class EvidenceRef(BaseModel):
    source_type: Literal["timeline_event", "patient_statement", "clinical_guideline"]
    source_id: uuid.UUID | str
    summary: str  # human-readable, not the raw record


class MissingInformation(BaseModel):
    event_type: str
    reason: str
    severity: Literal["low", "medium", "high"]


class Contradiction(BaseModel):
    id: uuid.UUID
    statement: str
    contradicting_evidence: list[EvidenceRef]
    detected_at: datetime
    # Only "objective" in Sprint 3 — "possible_inconsistency" and
    # "clinical_reasoning" are reserved for Sprint 5/6. Nothing produces a
    # Contradiction yet in Milestone 3.1; the model exists so Milestone 3.2
    # doesn't need a schema change to start populating it.
    category: Literal["objective"]
