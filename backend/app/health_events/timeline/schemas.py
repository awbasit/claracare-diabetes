import uuid
from collections.abc import Callable
from datetime import date, datetime
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Field

from app.health_events.models.enums import (
    EventSource,
    EventType,
    ExerciseIntensity,
    GlucoseReadingType,
    GlucoseUnit,
    MealType,
    Mood,
    SleepQuality,
    SymptomSeverity,
    SymptomType,
)
from app.health_events.models.exercise_log import ExerciseLog
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.meal_log import MealLog
from app.health_events.models.medication_log import MedicationLog
from app.health_events.models.sleep_log import SleepLog
from app.health_events.models.stress_log import StressLog
from app.health_events.models.symptom_log import SymptomLog
from app.health_events.models.vitals_log import VitalsLog

# --- Per-type detail payloads -----------------------------------------------
# Each carries its own `event_type` literal so the union below can discriminate
# on it — the frontend switches once on the envelope's event_type and gets a
# correctly-shaped `detail` for free, instead of switching per field name.


class GlucoseDetail(BaseModel):
    event_type: Literal[EventType.glucose] = EventType.glucose
    value: float
    unit: GlucoseUnit
    reading_type: GlucoseReadingType
    confidence: float | None
    manually_entered: bool


class MealDetail(BaseModel):
    event_type: Literal[EventType.meal] = EventType.meal
    meal_type: MealType
    food_items: str
    estimated_carbs_g: float | None
    estimated_calories: int | None
    portion_size: str | None
    drink: str | None


class MedicationDetail(BaseModel):
    event_type: Literal[EventType.medication] = EventType.medication
    medication_id: uuid.UUID
    scheduled_time: datetime | None
    actual_time: datetime
    taken: bool
    missed_reason: str | None


class ExerciseDetail(BaseModel):
    event_type: Literal[EventType.exercise] = EventType.exercise
    exercise_type: str
    duration_minutes: int
    intensity: ExerciseIntensity
    calories_burned: int | None
    heart_rate_avg: int | None


class SleepDetail(BaseModel):
    event_type: Literal[EventType.sleep] = EventType.sleep
    bedtime: datetime
    wake_time: datetime
    hours_slept: float
    quality: SleepQuality
    night_awakenings: int


class StressDetail(BaseModel):
    event_type: Literal[EventType.stress] = EventType.stress
    stress_level: int
    mood: Mood
    energy_level: int | None


class SymptomDetail(BaseModel):
    event_type: Literal[EventType.symptom] = EventType.symptom
    symptom_type: SymptomType
    severity: SymptomSeverity
    duration_notes: str | None


class VitalsDetail(BaseModel):
    event_type: Literal[EventType.vitals] = EventType.vitals
    weight_kg: float | None
    blood_pressure_systolic: int | None
    blood_pressure_diastolic: int | None
    heart_rate: int | None


TimelineDetail = Annotated[
    GlucoseDetail
    | MealDetail
    | MedicationDetail
    | ExerciseDetail
    | SleepDetail
    | StressDetail
    | SymptomDetail
    | VitalsDetail,
    Field(discriminator="event_type"),
]


def build_glucose_detail(detail: GlucoseLog) -> GlucoseDetail:
    return GlucoseDetail(
        value=detail.value,
        unit=detail.unit,
        reading_type=detail.reading_type,
        confidence=detail.confidence,
        manually_entered=detail.manually_entered,
    )


def _build_meal_detail(detail: MealLog) -> MealDetail:
    return MealDetail(
        meal_type=detail.meal_type,
        food_items=detail.food_items,
        estimated_carbs_g=detail.estimated_carbs_g,
        estimated_calories=detail.estimated_calories,
        portion_size=detail.portion_size,
        drink=detail.drink,
    )


def _build_medication_detail(detail: MedicationLog) -> MedicationDetail:
    return MedicationDetail(
        medication_id=detail.medication_id,
        scheduled_time=detail.scheduled_time,
        actual_time=detail.actual_time,
        taken=detail.taken,
        missed_reason=detail.missed_reason,
    )


def _build_exercise_detail(detail: ExerciseLog) -> ExerciseDetail:
    return ExerciseDetail(
        exercise_type=detail.exercise_type,
        duration_minutes=detail.duration_minutes,
        intensity=detail.intensity,
        calories_burned=detail.calories_burned,
        heart_rate_avg=detail.heart_rate_avg,
    )


def _build_sleep_detail(detail: SleepLog) -> SleepDetail:
    return SleepDetail(
        bedtime=detail.bedtime,
        wake_time=detail.wake_time,
        hours_slept=detail.hours_slept,
        quality=detail.quality,
        night_awakenings=detail.night_awakenings,
    )


def _build_stress_detail(detail: StressLog) -> StressDetail:
    return StressDetail(
        stress_level=detail.stress_level,
        mood=detail.mood,
        energy_level=detail.energy_level,
    )


def _build_symptom_detail(detail: SymptomLog) -> SymptomDetail:
    return SymptomDetail(
        symptom_type=detail.symptom_type,
        severity=detail.severity,
        duration_notes=detail.duration_notes,
    )


def _build_vitals_detail(detail: VitalsLog) -> VitalsDetail:
    return VitalsDetail(
        weight_kg=detail.weight_kg,
        blood_pressure_systolic=detail.blood_pressure_systolic,
        blood_pressure_diastolic=detail.blood_pressure_diastolic,
        heart_rate=detail.heart_rate,
    )


_DETAIL_BUILDERS: dict[EventType, Callable[[Any], BaseModel]] = {
    EventType.glucose: build_glucose_detail,
    EventType.meal: _build_meal_detail,
    EventType.medication: _build_medication_detail,
    EventType.exercise: _build_exercise_detail,
    EventType.sleep: _build_sleep_detail,
    EventType.stress: _build_stress_detail,
    EventType.symptom: _build_symptom_detail,
    EventType.vitals: _build_vitals_detail,
}


class TimelineEventRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_type: EventType
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime
    detail: TimelineDetail

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: Any) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_type=event.event_type,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            detail=_DETAIL_BUILDERS[event.event_type](detail),
        )


class DailySummary(BaseModel):
    date: date
    event_counts: dict[EventType, int]
    total_events: int
    medications_taken: int
    medications_missed: int
    latest_glucose: GlucoseDetail | None
    latest_glucose_timestamp: datetime | None
    glucose_average_mg_dl: float | None
    total_exercise_minutes: int
    average_stress_level: float | None
