import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaselineAssessmentBase(BaseModel):
    completed_at: datetime | None = None
    notes: str | None = None
    raw_answers: dict[str, Any] = {}


class BaselineAssessmentCreate(BaselineAssessmentBase):
    patient_id: uuid.UUID


class BaselineAssessmentUpdate(BaselineAssessmentBase):
    pass


class BaselineAssessmentRead(BaselineAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
