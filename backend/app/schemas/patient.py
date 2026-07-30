import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Sex


class PatientBase(BaseModel):
    age: int | None = None
    sex: Sex | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    occupation: str | None = None
    work_schedule: str | None = None


class PatientCreate(PatientBase):
    user_id: uuid.UUID


class PatientUpdate(PatientBase):
    pass


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    bmi: float | None = None
    created_at: datetime
    updated_at: datetime
