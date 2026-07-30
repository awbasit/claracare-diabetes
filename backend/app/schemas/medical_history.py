import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import DiabetesType


class MedicalHistoryBase(BaseModel):
    diabetes_type: DiabetesType | None = None
    years_since_diagnosis: int | None = None
    family_history: bool = False
    family_history_notes: str | None = None
    latest_hba1c: float | None = None
    latest_blood_pressure_systolic: int | None = None
    latest_blood_pressure_diastolic: int | None = None
    latest_cholesterol: float | None = None
    has_kidney_disease: bool = False
    has_eye_disease: bool = False
    has_neuropathy: bool = False
    comorbidities: list[str] = []


class MedicalHistoryCreate(MedicalHistoryBase):
    patient_id: uuid.UUID


class MedicalHistoryUpdate(MedicalHistoryBase):
    pass


class MedicalHistoryRead(MedicalHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
