import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicationBase(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    time_of_day: str | None = None
    purpose: str | None = None
    prescribed_by: str | None = None
    duration: str | None = None
    side_effects: str | None = None
    missed_doses_notes: str | None = None
    is_active: bool = True


class MedicationCreate(MedicationBase):
    patient_id: uuid.UUID


class MedicationUpdate(BaseModel):
    name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    time_of_day: str | None = None
    purpose: str | None = None
    prescribed_by: str | None = None
    duration: str | None = None
    side_effects: str | None = None
    missed_doses_notes: str | None = None
    is_active: bool | None = None


class MedicationRead(MedicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
