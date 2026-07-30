import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LifestyleProfileBase(BaseModel):
    sleep_hours_avg: float | None = None
    exercise_frequency: str | None = None
    exercise_type: str | None = None
    smoking_status: str | None = None
    alcohol_use: str | None = None
    stress_level_baseline: int | None = Field(default=None, ge=1, le=10)
    meal_schedule_notes: str | None = None


class LifestyleProfileCreate(LifestyleProfileBase):
    patient_id: uuid.UUID


class LifestyleProfileUpdate(LifestyleProfileBase):
    pass


class LifestyleProfileRead(LifestyleProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
