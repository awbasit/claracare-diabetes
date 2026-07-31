"""Return types for the Clinical Reasoning Service's live-query methods
(Milestone 3.2's Clinical Tool Layer) — distinct from PatientContext's
fields because these answer "what's true right now" from HealthEvent
directly, not "what did the last snapshot say".
"""

from datetime import datetime

from pydantic import BaseModel

from app.clinical_reasoning.schemas.context import GlucoseReading, SymptomSummary
from app.health_events.models.enums import MealType


class TodayGlucoseSummary(BaseModel):
    readings: list[GlucoseReading]
    count: int
    average_mg_dl: float | None


class MealEntry(BaseModel):
    meal_type: MealType
    food_items: str
    estimated_carbs_g: float | None
    timestamp: datetime


class RecentMealsSummary(BaseModel):
    period_days: int
    meals: list[MealEntry]
    count: int


class MedicationAdherenceSummary(BaseModel):
    period_days: int
    doses_taken: int
    doses_missed: int
    adherence_pct: float | None


class SleepSummary(BaseModel):
    period_days: int
    nights_logged: int
    average_hours: float | None
    last_night_hours: float | None
    average_quality_score: float | None


class LatestVitalsSummary(BaseModel):
    weight_kg: float | None
    blood_pressure_systolic: int | None
    blood_pressure_diastolic: int | None
    heart_rate: int | None
    logged_at: datetime


class RecentSymptomsSummary(BaseModel):
    period_days: int
    symptoms: list[SymptomSummary]
    count: int


__all__ = [
    "LatestVitalsSummary",
    "MealEntry",
    "MedicationAdherenceSummary",
    "RecentMealsSummary",
    "RecentSymptomsSummary",
    "SleepSummary",
    "TodayGlucoseSummary",
]
