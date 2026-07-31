import uuid
from datetime import UTC, datetime

from app.clinical_reasoning.services.evidence_builder import build_evidence_ref
from app.health_events.models.enums import (
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
from app.models.medication import Medication

# A fixed, known Wednesday — every test asserts against this exact weekday
# rather than deriving it, so a bug in build_evidence_ref's own weekday
# formatting would still be caught.
_WEDNESDAY = datetime(2026, 1, 7, 8, 0, tzinfo=UTC)


def _health_event(event_type: EventType, **detail_kwargs: object) -> HealthEvent:
    event = HealthEvent(
        id=uuid.uuid4(), patient_id=uuid.uuid4(), event_type=event_type, event_timestamp=_WEDNESDAY
    )
    for field, value in detail_kwargs.items():
        setattr(event, field, value)
    return event


def test_evidence_ref_glucose() -> None:
    event = _health_event(
        EventType.glucose,
        glucose_log=GlucoseLog(
            value=110, unit=GlucoseUnit.mg_dl, reading_type=GlucoseReadingType.fasting
        ),
    )
    ref = build_evidence_ref(event)
    assert ref.source_type == "timeline_event"
    assert ref.source_id == event.id
    assert ref.summary == "Glucose 110 mg/dL (fasting), Wednesday"


def test_evidence_ref_meal() -> None:
    event = _health_event(
        EventType.meal,
        meal_log=MealLog(meal_type=MealType.breakfast, food_items="Oatmeal and eggs"),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "Breakfast logged: Oatmeal and eggs, Wednesday"


def test_evidence_ref_medication_missed() -> None:
    medication = Medication(id=uuid.uuid4(), patient_id=uuid.uuid4(), name="Metformin")
    event = _health_event(
        EventType.medication,
        medication_log=MedicationLog(
            actual_time=_WEDNESDAY, taken=False, medication_id=medication.id, medication=medication
        ),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "Missed Metformin, Wednesday"


def test_evidence_ref_medication_taken() -> None:
    medication = Medication(id=uuid.uuid4(), patient_id=uuid.uuid4(), name="Metformin")
    event = _health_event(
        EventType.medication,
        medication_log=MedicationLog(
            actual_time=_WEDNESDAY, taken=True, medication_id=medication.id, medication=medication
        ),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "Took Metformin, Wednesday"


def test_evidence_ref_exercise() -> None:
    event = _health_event(
        EventType.exercise,
        exercise_log=ExerciseLog(
            exercise_type="Running", duration_minutes=30, intensity=ExerciseIntensity.moderate
        ),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "30 min Running (moderate), Wednesday"


def test_evidence_ref_sleep() -> None:
    event = _health_event(
        EventType.sleep,
        sleep_log=SleepLog(
            bedtime=_WEDNESDAY, wake_time=_WEDNESDAY, hours_slept=7.5, quality=SleepQuality.good
        ),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "7.5h sleep (good), Wednesday"


def test_evidence_ref_stress() -> None:
    event = _health_event(EventType.stress, stress_log=StressLog(stress_level=4, mood=Mood.neutral))
    ref = build_evidence_ref(event)
    assert ref.summary == "Stress level 4 (neutral mood), Wednesday"


def test_evidence_ref_symptom() -> None:
    event = _health_event(
        EventType.symptom,
        symptom_log=SymptomLog(symptom_type=SymptomType.fatigue, severity=SymptomSeverity.mild),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "Fatigue (mild), Wednesday"


def test_evidence_ref_vitals_all_fields() -> None:
    event = _health_event(
        EventType.vitals,
        vitals_log=VitalsLog(
            weight_kg=72.5, blood_pressure_systolic=118, blood_pressure_diastolic=76, heart_rate=68
        ),
    )
    ref = build_evidence_ref(event)
    assert ref.summary == "Weight 72.5 kg, BP 118/76, HR 68, Wednesday"


def test_evidence_ref_vitals_partial_fields() -> None:
    event = _health_event(EventType.vitals, vitals_log=VitalsLog(heart_rate=70))
    ref = build_evidence_ref(event)
    assert ref.summary == "HR 70, Wednesday"


def test_evidence_ref_vitals_no_fields() -> None:
    event = _health_event(EventType.vitals, vitals_log=VitalsLog())
    ref = build_evidence_ref(event)
    assert ref.summary == "Vitals logged, Wednesday"
