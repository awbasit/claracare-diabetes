import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.clinical_reasoning.services.confidence_calculators import (
    _COLD_START_RELIABILITY,
    _DEFAULT_RELIABILITY,
    ExerciseConfidenceCalculator,
    GlucoseConfidenceCalculator,
    MealConfidenceCalculator,
    MedicationConfidenceCalculator,
    SleepConfidenceCalculator,
    StressConfidenceCalculator,
    SymptomConfidenceCalculator,
)
from app.health_events.models.enums import (
    EventSource,
    EventType,
    GlucoseReadingType,
    GlucoseUnit,
    Mood,
    SleepQuality,
)
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.medication_log import MedicationLog
from app.health_events.models.sleep_log import SleepLog
from app.health_events.models.stress_log import StressLog
from app.models.medication import Medication
from app.models.patient import Patient

_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)


def _patient(*, created_at: datetime, medications: list[Medication] | None = None) -> Patient:
    return Patient(
        id=uuid.uuid4(), user_id=uuid.uuid4(), created_at=created_at, medications=medications or []
    )


def _medication(name: str, *, frequency: str | None = None, is_active: bool = True) -> Medication:
    return Medication(
        id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        name=name,
        frequency=frequency,
        is_active=is_active,
    )


def _event(
    event_type: EventType, event_timestamp: datetime, **detail_kwargs: object
) -> HealthEvent:
    event = HealthEvent(
        id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        event_type=event_type,
        event_timestamp=event_timestamp,
        source=EventSource.manual,
    )
    for field, value in detail_kwargs.items():
        setattr(event, field, value)
    return event


# --- MedicationConfidenceCalculator --------------------------------------------


def test_medication_completeness_ratio_over_last_24h() -> None:
    metformin = _medication("Metformin", frequency="once daily")
    insulin = _medication("Insulin Glargine", frequency="twice daily")
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[metformin, insulin])
    data = [
        _event(
            EventType.medication,
            _NOW - timedelta(hours=1),
            medication_log=MedicationLog(actual_time=_NOW, taken=True, medication_id=metformin.id),
        ),
        _event(
            EventType.medication,
            _NOW - timedelta(hours=2),
            medication_log=MedicationLog(actual_time=_NOW, taken=True, medication_id=insulin.id),
        ),
        _event(
            EventType.medication,
            _NOW - timedelta(hours=3),
            medication_log=MedicationLog(actual_time=_NOW, taken=False, medication_id=insulin.id),
        ),
    ]
    quality = MedicationConfidenceCalculator(now=_NOW).calculate(patient, data)
    # expected_doses = 1 (metformin) + 2 (insulin) = 3; logged_taken = 2 (missed dose doesn't count)
    assert quality.completeness == pytest.approx(2 / 3, abs=0.01)
    assert quality.consistency == 1.0
    assert quality.reliability == _DEFAULT_RELIABILITY
    assert quality.coverage_label is None


def test_medication_completeness_ignores_doses_outside_24h_window() -> None:
    metformin = _medication("Metformin", frequency="once daily")
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[metformin])
    data = [
        # Six taken doses, all from 30h+ ago — outside the 24h completeness
        # window, so they must not mask today's missing dose.
        _event(
            EventType.medication,
            _NOW - timedelta(hours=30 + i),
            medication_log=MedicationLog(actual_time=_NOW, taken=True, medication_id=metformin.id),
        )
        for i in range(6)
    ]
    quality = MedicationConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.completeness == 0.0


def test_medication_completeness_is_trivially_full_with_no_active_medications() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[])
    quality = MedicationConfidenceCalculator(now=_NOW).calculate(patient, [])
    assert quality.completeness == 1.0


# --- GlucoseConfidenceCalculator ------------------------------------------------


def test_glucose_completeness_for_oral_regimen() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[])
    data = [
        _event(
            EventType.glucose,
            _NOW - timedelta(hours=2),
            glucose_log=GlucoseLog(
                value=100, unit=GlucoseUnit.mg_dl, reading_type=GlucoseReadingType.fasting
            ),
        )
    ]
    quality = GlucoseConfidenceCalculator(now=_NOW).calculate(patient, data)
    # oral_or_none regimen expects 1/day; one reading today -> complete.
    assert quality.completeness == 1.0


def test_glucose_completeness_zero_with_no_readings() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[])
    quality = GlucoseConfidenceCalculator(now=_NOW).calculate(patient, [])
    assert quality.completeness == 0.0
    assert quality.freshness == 0.0


def test_glucose_completeness_requires_four_per_day_for_basal_bolus() -> None:
    insulin_a = _medication("Insulin Glargine", frequency="once daily")
    insulin_b = _medication("Insulin Lispro", frequency="before meals")
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[insulin_a, insulin_b])
    data = [
        _event(
            EventType.glucose,
            _NOW - timedelta(hours=h),
            glucose_log=GlucoseLog(
                value=100, unit=GlucoseUnit.mg_dl, reading_type=GlucoseReadingType.fasting
            ),
        )
        for h in (1, 5)
    ]
    quality = GlucoseConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.completeness == pytest.approx(2 / 4, abs=0.01)


def test_glucose_consistency_flags_outlier_against_own_history() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[])
    history_values = [90, 100, 110]
    data = [
        _event(
            EventType.glucose,
            _NOW - timedelta(days=i + 1),
            glucose_log=GlucoseLog(
                value=v, unit=GlucoseUnit.mg_dl, reading_type=GlucoseReadingType.fasting
            ),
        )
        for i, v in enumerate(history_values)
    ]
    data.append(
        _event(
            EventType.glucose,
            _NOW - timedelta(hours=1),
            glucose_log=GlucoseLog(
                value=300, unit=GlucoseUnit.mg_dl, reading_type=GlucoseReadingType.fasting
            ),
        )
    )
    quality = GlucoseConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.consistency == pytest.approx(0.0, abs=0.01)


def test_glucose_consistency_normalizes_mixed_units() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100), medications=[])
    data = [
        _event(
            EventType.glucose,
            _NOW - timedelta(days=1),
            glucose_log=GlucoseLog(
                value=100, unit=GlucoseUnit.mg_dl, reading_type=GlucoseReadingType.fasting
            ),
        ),
        _event(
            EventType.glucose,
            _NOW - timedelta(hours=1),
            # ~5.5 mmol/L is ~99 mg/dL — should read as consistent with the history above.
            glucose_log=GlucoseLog(
                value=5.5, unit=GlucoseUnit.mmol_l, reading_type=GlucoseReadingType.fasting
            ),
        ),
    ]
    quality = GlucoseConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.consistency == 1.0


# --- Baseline calculators: cold start (§6, §12 item 3) -------------------------


def test_meal_calculator_uses_population_default_under_14_days_of_history() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=5))  # cold start
    data = [_event(EventType.meal, _NOW - timedelta(days=1))]
    quality = MealConfidenceCalculator(now=_NOW).calculate(patient, data)
    # Fired via reliability, not completeness — cold start is provisional.
    assert quality.reliability == _COLD_START_RELIABILITY
    # population default: 3/day * 7 recent days = 21 expected; 1 logged.
    assert quality.completeness == pytest.approx(1 / 21, abs=0.01)


def test_meal_calculator_switches_to_patient_baseline_after_14_days() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=20))  # past cold start
    # One meal/day for the full 30-day baseline window -> baseline = 1/day.
    data = [_event(EventType.meal, _NOW - timedelta(days=i)) for i in range(1, 31)]
    quality = MealConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.reliability == _DEFAULT_RELIABILITY
    # baseline 1/day * 7 recent days = 7 expected; 7 of the last 7 days logged.
    assert quality.completeness == pytest.approx(1.0, abs=0.01)


def test_sleep_calculator_consistency_flags_unusual_hours() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100))
    data = [
        _event(
            EventType.sleep,
            _NOW - timedelta(days=3),
            sleep_log=SleepLog(
                bedtime=_NOW, wake_time=_NOW, hours_slept=7.0, quality=SleepQuality.good
            ),
        ),
        _event(
            EventType.sleep,
            _NOW - timedelta(days=2),
            sleep_log=SleepLog(
                bedtime=_NOW, wake_time=_NOW, hours_slept=7.5, quality=SleepQuality.good
            ),
        ),
        _event(
            EventType.sleep,
            _NOW - timedelta(hours=6),
            sleep_log=SleepLog(
                bedtime=_NOW, wake_time=_NOW, hours_slept=1.0, quality=SleepQuality.poor
            ),
        ),
    ]
    quality = SleepConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.consistency < 0.5


def test_stress_calculator_cold_start_reliability_and_completeness() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=2))  # very much cold start
    data = [
        _event(
            EventType.stress,
            _NOW - timedelta(hours=3),
            stress_log=StressLog(stress_level=5, mood=Mood.neutral),
        )
    ]
    quality = StressConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.reliability == _COLD_START_RELIABILITY
    # population default 1/day * 7 = 7 expected; 1 logged.
    assert quality.completeness == pytest.approx(1 / 7, abs=0.01)


# --- Coverage-only calculators (§6) ---------------------------------------------


@pytest.mark.parametrize(
    ("count", "expected_label", "expected_completeness"),
    [(0, "unknown", 0.0), (1, "low", 0.33), (3, "moderate", 0.66), (5, "high", 1.0)],
)
def test_exercise_coverage_label_thresholds(
    count: int, expected_label: str, expected_completeness: float
) -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100))
    data = [_event(EventType.exercise, _NOW - timedelta(days=i)) for i in range(count)]
    quality = ExerciseConfidenceCalculator(now=_NOW).calculate(patient, data)
    assert quality.coverage_label == expected_label
    assert quality.completeness == pytest.approx(expected_completeness, abs=0.01)


def test_symptom_coverage_label_unknown_with_no_data() -> None:
    patient = _patient(created_at=_NOW - timedelta(days=100))
    quality = SymptomConfidenceCalculator(now=_NOW).calculate(patient, [])
    assert quality.coverage_label == "unknown"
    assert quality.freshness == 0.0
