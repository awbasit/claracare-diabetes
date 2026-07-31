import re
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from app.clinical_reasoning.schemas.data_quality import (
    CoverageLabel,
    DataQuality,
    DataQualityReport,
)
from app.clinical_reasoning.services.glucose_regimen import determine_glucose_regimen
from app.clinical_reasoning.services.quality_utils import consistency_score, freshness
from app.health_events.glucose.service import mmol_l_to_mg_dl
from app.health_events.models.enums import EventSource, EventType, GlucoseUnit
from app.health_events.models.health_event import HealthEvent
from app.models.patient import Patient

# --- Shared constants & helpers ---------------------------------------------

# manual entries default to a fixed reliability score; imported (future
# wearable data) would score differently once that exists (§7) — not used
# yet since Sprint 1/2 only ever writes source=manual, but the mapping
# exists so Sprint 4+ doesn't need a schema change when imported data
# arrives.
_RELIABILITY_BY_SOURCE: dict[EventSource, float] = {
    EventSource.manual: 0.9,
    EventSource.imported: 0.7,
}
_DEFAULT_RELIABILITY = _RELIABILITY_BY_SOURCE[EventSource.manual]

# §12 open item 3: 14 days minimum before trusting a patient-specific
# baseline over the population default, then a 30-day trailing window.
_COLD_START_DAYS = 14
_BASELINE_WINDOW_DAYS = 30
_RECENT_WINDOW_DAYS = 7

# Population defaults (§6) used during cold-start.
_POPULATION_DEFAULT_PER_DAY = {"meal": 3, "sleep": 1, "stress": 1}
_COLD_START_RELIABILITY = 0.6  # lower, since the expectation itself is provisional


def _reliability_from_events(events: list[HealthEvent]) -> float:
    if not events:
        return _DEFAULT_RELIABILITY
    scores = [_RELIABILITY_BY_SOURCE.get(event.source, _DEFAULT_RELIABILITY) for event in events]
    return round(sum(scores) / len(scores), 2)


def _latest_timestamp(events: list[HealthEvent]) -> datetime | None:
    if not events:
        return None
    return max(event.event_timestamp for event in events)


_FREQUENCY_WORDS: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"\b(once|1x|one time)\b"), 1),
    (re.compile(r"\b(twice|2x|two times)\b"), 2),
    (re.compile(r"\b(three times|thrice|3x)\b"), 3),
    (re.compile(r"\b(four times|4x)\b"), 4),
]


def _parse_daily_frequency(frequency: str | None) -> int:
    """Sprint 1's Medication.frequency is free text (e.g. "twice daily"),
    not a structured schedule — this recognizes a few common phrasings and
    otherwise assumes once/day, which is the safer (lower) default for a
    completeness ratio than assuming a high expectation the patient was
    never actually told to meet.
    """
    if not frequency:
        return 1
    lowered = frequency.lower()
    for pattern, count in _FREQUENCY_WORDS:
        if pattern.search(lowered):
            return count
    return 1


def _coverage_label_from_count(count: int) -> CoverageLabel:
    if count == 0:
        return (
            "unknown"  # absence isn't evidence of poor logging — could just mean nothing happened
        )
    if count <= 2:
        return "low"
    if count <= 4:
        return "moderate"
    return "high"


_COMPLETENESS_BY_COVERAGE: dict[CoverageLabel, float] = {
    "unknown": 0.0,
    "low": 0.33,
    "moderate": 0.66,
    "high": 1.0,
}


# --- Base class --------------------------------------------------------------


class ConfidenceCalculator(ABC):
    @abstractmethod
    def calculate(self, patient: Patient, data: list[HealthEvent]) -> DataQuality: ...


# --- Deterministic, non-baseline calculators ---------------------------------


class MedicationConfidenceCalculator(ConfidenceCalculator):
    """completeness = logged_doses / expected_doses, where expected_doses
    comes straight from the prescribed medication list — no cold start, the
    expectation is prescribed, not learned. expected_doses is a per-day
    figure, so logged_doses is counted over the trailing 24h specifically
    (not however wide a window the orchestrator happened to fetch) —
    otherwise a week of good days would mask one bad one.
    """

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def calculate(self, patient: Patient, data: list[HealthEvent]) -> DataQuality:
        now = self._now or datetime.now(UTC)
        day_ago = now - timedelta(hours=24)

        active_medications = [m for m in patient.medications if m.is_active]
        expected_doses = sum(_parse_daily_frequency(m.frequency) for m in active_medications)
        logged_taken = sum(
            1
            for event in data
            if event.event_timestamp >= day_ago
            and event.medication_log is not None
            and event.medication_log.taken
        )
        completeness = min(1.0, logged_taken / expected_doses) if expected_doses > 0 else 1.0

        return DataQuality(
            completeness=round(completeness, 2),
            freshness=freshness(_latest_timestamp(data), staleness_threshold_hours=24.0, now=now),
            consistency=1.0,  # taken/missed is boolean — no plausibility check applies
            reliability=_reliability_from_events(data),
            coverage_label=None,
        )


class GlucoseConfidenceCalculator(ConfidenceCalculator):
    """completeness via the insulin-regimen lookup table — no cold start,
    it's a clinical lookup against data already on file, not a learned
    baseline.
    """

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def calculate(self, patient: Patient, data: list[HealthEvent]) -> DataQuality:
        regimen = determine_glucose_regimen(patient.medications)
        now = self._now or datetime.now(UTC)
        day_ago = now - timedelta(hours=24)

        logged_today = sum(1 for event in data if event.event_timestamp >= day_ago)
        completeness = min(1.0, logged_today / regimen.expected_readings_per_day)

        # Compare the most recent reading against the rest of the window.
        consistency = 1.0
        events_with_values = [
            (event.event_timestamp, event.glucose_log) for event in data if event.glucose_log
        ]
        if events_with_values:
            events_with_values.sort(key=lambda pair: pair[0], reverse=True)
            latest_log = events_with_values[0][1]
            latest_mg_dl = (
                latest_log.value
                if latest_log.unit == GlucoseUnit.mg_dl
                else mmol_l_to_mg_dl(latest_log.value)
            )
            history_mg_dl = [
                log.value if log.unit == GlucoseUnit.mg_dl else mmol_l_to_mg_dl(log.value)
                for _, log in events_with_values[1:]
            ]
            consistency = consistency_score(latest_mg_dl, history_mg_dl)

        return DataQuality(
            completeness=round(completeness, 2),
            freshness=freshness(
                _latest_timestamp(data), staleness_threshold_hours=regimen.staleness_hours, now=now
            ),
            consistency=round(consistency, 2),
            reliability=_reliability_from_events(data),
            coverage_label=None,
        )


# --- Baseline calculators with cold-start (§6) --------------------------------


class _BaselineCalculator(ConfidenceCalculator, ABC):
    """Shared cold-start machinery for Meal/Sleep/Stress: population default
    until the patient has been in the system 14+ days, then their own
    trailing-30-day average. `data` is expected to be the full 30-day
    window; completeness compares the most recent 7 days against that
    baseline (comparing a window against itself would be trivially ~1.0).
    """

    event_type: str
    staleness_hours: float

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def calculate(self, patient: Patient, data: list[HealthEvent]) -> DataQuality:
        now = self._now or datetime.now(UTC)
        days_since_registered = (now.date() - patient.created_at.date()).days
        is_cold_start = days_since_registered < _COLD_START_DAYS

        if is_cold_start:
            expected_per_day = float(_POPULATION_DEFAULT_PER_DAY[self.event_type])
            reliability = _COLD_START_RELIABILITY
        else:
            expected_per_day = len(data) / _BASELINE_WINDOW_DAYS
            if expected_per_day <= 0:
                expected_per_day = float(_POPULATION_DEFAULT_PER_DAY[self.event_type])
            reliability = _reliability_from_events(data)

        recent_cutoff = now - timedelta(days=_RECENT_WINDOW_DAYS)
        recent_count = sum(1 for event in data if event.event_timestamp >= recent_cutoff)
        expected_recent = expected_per_day * _RECENT_WINDOW_DAYS
        completeness = min(1.0, recent_count / expected_recent) if expected_recent > 0 else 1.0

        return DataQuality(
            completeness=round(completeness, 2),
            freshness=freshness(
                _latest_timestamp(data), staleness_threshold_hours=self.staleness_hours, now=now
            ),
            consistency=round(self._consistency(data), 2),
            reliability=reliability,
            coverage_label=None,
        )

    def _consistency(self, data: list[HealthEvent]) -> float:
        return 1.0


class MealConfidenceCalculator(_BaselineCalculator):
    event_type = "meal"
    staleness_hours = 24.0
    # No single clean numeric value on most meal entries (estimated_carbs_g
    # is frequently null) to run an outlier check against — left at the
    # base class's constant 1.0.


class SleepConfidenceCalculator(_BaselineCalculator):
    event_type = "sleep"
    staleness_hours = 30.0  # logged the morning after — allow a bit past 24h

    def _consistency(self, data: list[HealthEvent]) -> float:
        events_with_hours = [
            (event.event_timestamp, event.sleep_log.hours_slept)
            for event in data
            if event.sleep_log
        ]
        if not events_with_hours:
            return 1.0
        events_with_hours.sort(key=lambda pair: pair[0], reverse=True)
        latest = events_with_hours[0][1]
        history = [hours for _, hours in events_with_hours[1:]]
        return consistency_score(latest, history)


class StressConfidenceCalculator(_BaselineCalculator):
    event_type = "stress"
    staleness_hours = 24.0

    def _consistency(self, data: list[HealthEvent]) -> float:
        events_with_level = [
            (event.event_timestamp, event.stress_log.stress_level)
            for event in data
            if event.stress_log
        ]
        if not events_with_level:
            return 1.0
        events_with_level.sort(key=lambda pair: pair[0], reverse=True)
        latest = events_with_level[0][1]
        history = [float(level) for _, level in events_with_level[1:]]
        return consistency_score(float(latest), history)


# --- Coverage-only calculators (§6) -------------------------------------------


class _CoverageCalculator(ConfidenceCalculator, ABC):
    """No completeness ratio — absence of exercise/symptom data isn't
    evidence of poor logging, it may just mean nothing happened. `data` is
    expected to be a 7-day window.
    """

    staleness_hours = 168.0  # 7 days — these types aren't expected daily

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def calculate(self, patient: Patient, data: list[HealthEvent]) -> DataQuality:
        coverage_label = _coverage_label_from_count(len(data))
        return DataQuality(
            completeness=_COMPLETENESS_BY_COVERAGE[coverage_label],
            freshness=freshness(
                _latest_timestamp(data),
                staleness_threshold_hours=self.staleness_hours,
                now=self._now,
            ),
            consistency=1.0,
            reliability=_reliability_from_events(data),
            coverage_label=coverage_label,
        )


class ExerciseConfidenceCalculator(_CoverageCalculator):
    pass


class SymptomConfidenceCalculator(_CoverageCalculator):
    pass


# --- Fetch + orchestration ----------------------------------------------------

_DETAIL_RELATIONSHIP: dict[EventType, InstrumentedAttribute[Any]] = {
    EventType.glucose: HealthEvent.glucose_log,
    EventType.meal: HealthEvent.meal_log,
    EventType.medication: HealthEvent.medication_log,
    EventType.exercise: HealthEvent.exercise_log,
    EventType.sleep: HealthEvent.sleep_log,
    EventType.stress: HealthEvent.stress_log,
    EventType.symptom: HealthEvent.symptom_log,
    EventType.vitals: HealthEvent.vitals_log,
}

_CALCULATORS: dict[EventType, tuple[ConfidenceCalculator, int]] = {
    EventType.medication: (MedicationConfidenceCalculator(), _RECENT_WINDOW_DAYS),
    EventType.glucose: (GlucoseConfidenceCalculator(), _RECENT_WINDOW_DAYS),
    EventType.meal: (MealConfidenceCalculator(), _BASELINE_WINDOW_DAYS),
    EventType.sleep: (SleepConfidenceCalculator(), _BASELINE_WINDOW_DAYS),
    EventType.stress: (StressConfidenceCalculator(), _BASELINE_WINDOW_DAYS),
    EventType.exercise: (ExerciseConfidenceCalculator(), _RECENT_WINDOW_DAYS),
    EventType.symptom: (SymptomConfidenceCalculator(), _RECENT_WINDOW_DAYS),
}


async def _load_patient_with_medications(db: AsyncSession, patient_id: uuid.UUID) -> Patient:
    result = await db.execute(
        select(Patient).options(selectinload(Patient.medications)).where(Patient.id == patient_id)
    )
    return result.scalar_one()


async def _load_events_with_detail(
    db: AsyncSession, patient_id: uuid.UUID, event_type: EventType, since: datetime
) -> list[HealthEvent]:
    result = await db.execute(
        select(HealthEvent)
        .options(selectinload(_DETAIL_RELATIONSHIP[event_type]))
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_type == event_type,
            HealthEvent.event_timestamp >= since,
        )
        .order_by(HealthEvent.event_timestamp.desc())
    )
    return list(result.scalars().all())


def _average(numbers: list[float]) -> float:
    return round(sum(numbers) / len(numbers), 2)


async def run_all_calculators(db: AsyncSession, patient_id: uuid.UUID) -> DataQualityReport:
    """Fetches each type's window with its detail row eagerly loaded (the
    calculators themselves are sync, per the ABC, so all I/O has to happen
    before calculate() is called), runs every calculator, and averages
    across types for the overall score (§12 open item 1: simple average).
    """
    now = datetime.now(UTC)
    patient = await _load_patient_with_medications(db, patient_id)

    by_type: dict[str, DataQuality] = {}
    for event_type, (calculator, window_days) in _CALCULATORS.items():
        since = now - timedelta(days=window_days)
        events = await _load_events_with_detail(db, patient_id, event_type, since)
        by_type[event_type.value] = calculator.calculate(patient, events)

    values = list(by_type.values())
    overall = DataQuality(
        completeness=_average([v.completeness for v in values]),
        freshness=_average([v.freshness for v in values]),
        consistency=_average([v.consistency for v in values]),
        reliability=_average([v.reliability for v in values]),
        coverage_label=None,
    )
    return DataQualityReport(by_type=by_type, overall=overall)
