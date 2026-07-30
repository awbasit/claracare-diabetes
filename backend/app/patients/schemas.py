from typing import Any

from pydantic import BaseModel

from app.schemas.lifestyle_profile import LifestyleProfileRead
from app.schemas.medical_history import MedicalHistoryRead
from app.schemas.medication import MedicationRead
from app.schemas.patient import PatientRead


class PatientProfileRead(BaseModel):
    patient: PatientRead
    medical_history: MedicalHistoryRead | None = None
    lifestyle_profile: LifestyleProfileRead | None = None
    medications: list[MedicationRead] = []


class BaselineAssessmentSubmit(BaseModel):
    notes: str | None = None
    raw_answers: dict[str, Any] = {}
