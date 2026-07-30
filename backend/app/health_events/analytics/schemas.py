from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.health_events.models.enums import GlucoseUnit

Period = Literal["week", "month"]


class DailyGlucoseTrendPoint(BaseModel):
    date: date
    average: float | None
    minimum: float | None
    maximum: float | None
    count: int


class DailyMealTrendPoint(BaseModel):
    date: date
    count: int
    average_carbs_g: float | None


class DailyMedicationTrendPoint(BaseModel):
    date: date
    taken_count: int
    missed_count: int
    adherence_pct: float | None


class DailyExerciseTrendPoint(BaseModel):
    date: date
    total_minutes: int
    session_count: int


class DailySleepTrendPoint(BaseModel):
    date: date
    average_hours: float | None
    average_quality_score: float | None


class DailyStressTrendPoint(BaseModel):
    date: date
    average_stress_level: float | None
    average_energy_level: float | None


class DailySymptomTrendPoint(BaseModel):
    date: date
    count: int


class DailyVitalsTrendPoint(BaseModel):
    date: date
    latest_weight_kg: float | None
    latest_blood_pressure_systolic: int | None
    latest_blood_pressure_diastolic: int | None


class TrendsResponse(BaseModel):
    period: Period
    start_date: date
    end_date: date
    glucose_unit: GlucoseUnit
    glucose: list[DailyGlucoseTrendPoint]
    meals: list[DailyMealTrendPoint]
    medication: list[DailyMedicationTrendPoint]
    exercise: list[DailyExerciseTrendPoint]
    sleep: list[DailySleepTrendPoint]
    stress: list[DailyStressTrendPoint]
    symptoms: list[DailySymptomTrendPoint]
    vitals: list[DailyVitalsTrendPoint]
