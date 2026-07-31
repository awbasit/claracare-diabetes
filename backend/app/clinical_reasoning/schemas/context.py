import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.health_events.models.enums import (
    GlucoseReadingType,
    GlucoseUnit,
    SymptomSeverity,
    SymptomType,
)
from app.models.enums import DiabetesType, Sex

# --- Nested summary types --------------------------------------------------
# The design doc (§3) names these types on PatientContext's fields but does
# not spec their internals — they're shaped here from what Sprint 1/2 data
# is actually available.


class DemographicsSummary(BaseModel):
    age: int | None
    sex: Sex | None
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    occupation: str | None
    work_schedule: str | None


class DiabetesHistorySummary(BaseModel):
    diabetes_type: DiabetesType | None
    years_since_diagnosis: int | None
    family_history: bool
    family_history_notes: str | None
    latest_hba1c: float | None
    latest_blood_pressure_systolic: int | None
    latest_blood_pressure_diastolic: int | None
    latest_cholesterol: float | None
    has_kidney_disease: bool
    has_eye_disease: bool
    has_neuropathy: bool
    comorbidities: list[str]


class MedicationSummary(BaseModel):
    id: uuid.UUID
    name: str
    dosage: str | None
    frequency: str | None
    time_of_day: str | None
    purpose: str | None
    is_active: bool
    # Most recent medication_log.actual_time for this medication, regardless
    # of taken/missed — lets MedicationAdherenceRule check "logged at all in
    # the last 24h" without a second DB round trip through the rule itself
    # (Rule.evaluate is sync and context-only, see services/rules.py).
    last_logged_at: datetime | None


class GlucoseReading(BaseModel):
    value: float
    unit: GlucoseUnit
    reading_type: GlucoseReadingType
    timestamp: datetime


class TimelineSummary(BaseModel):
    """Rollup over the trailing `period_days` (7), plus a few "most recent"
    markers that a pure aggregate can't answer (e.g. "was anything logged
    today") — sourced from Sprint 2's timeline/analytics services rather
    than raw tables, per the build_context() instructions.
    """

    period_days: int = 7
    total_events: int
    glucose_reading_count: int
    glucose_average_mg_dl: float | None
    glucose_stdev_mg_dl: float | None
    meals_logged_count: int
    meals_logged_today: int
    last_meal_at: datetime | None
    exercise_total_minutes: int
    exercise_session_count: int
    sleep_average_hours: float | None
    last_sleep_at: datetime | None
    average_stress_level: float | None
    symptoms_logged_count: int


class AdherenceSummary(BaseModel):
    doses_taken_7day: int
    doses_missed_7day: int
    adherence_pct_7day: float | None


class SymptomSummary(BaseModel):
    symptom_type: SymptomType
    severity: SymptomSeverity
    logged_at: datetime
    duration_notes: str | None


class LifestyleSummary(BaseModel):
    sleep_hours_avg: float | None
    exercise_frequency: str | None
    exercise_type: str | None
    smoking_status: str | None
    alcohol_use: str | None
    stress_level_baseline: int | None
    meal_schedule_notes: str | None


class PatientGoal(BaseModel):
    id: uuid.UUID
    goal: str
    context: str | None
    status: Literal["active", "achieved", "abandoned"]
    set_at: datetime
    source: Literal["patient_stated", "ai_suggested"]


# --- The context itself -----------------------------------------------------


class PatientContext(BaseModel):
    """Immutable, versioned. Every update produces a new version rather than
    mutating an existing one — see PatientContextSnapshot for how that's
    persisted.
    """

    patient_id: uuid.UUID
    version: int
    generated_at: datetime
    demographics: DemographicsSummary
    diabetes_history: DiabetesHistorySummary
    medications: list[MedicationSummary]
    latest_glucose: GlucoseReading | None
    last_7_day_summary: TimelineSummary
    adherence_summary: AdherenceSummary
    active_symptoms: list[SymptomSummary]
    lifestyle_summary: LifestyleSummary
    goals: list[PatientGoal]
    recent_patterns: list[str]  # populated in Sprint 4; always [] until then
    known_barriers: list[str]  # sourced from episodic memory, Milestone 3.3; always [] until then


__all__ = [
    "AdherenceSummary",
    "DemographicsSummary",
    "DiabetesHistorySummary",
    "GlucoseReading",
    "LifestyleSummary",
    "MedicationSummary",
    "PatientContext",
    "PatientGoal",
    "SymptomSummary",
    "TimelineSummary",
]
