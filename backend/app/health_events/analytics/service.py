import uuid
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.analytics.schemas import (
    DailyExerciseTrendPoint,
    DailyGlucoseTrendPoint,
    DailyMealTrendPoint,
    DailyMedicationTrendPoint,
    DailySleepTrendPoint,
    DailyStressTrendPoint,
    DailySymptomTrendPoint,
    DailyVitalsTrendPoint,
    Period,
    TrendsResponse,
)
from app.health_events.glucose.service import mg_dl_to_mmol_l, mmol_l_to_mg_dl
from app.health_events.models.enums import EventType, GlucoseUnit, SleepQuality
from app.health_events.models.exercise_log import ExerciseLog
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.meal_log import MealLog
from app.health_events.models.medication_log import MedicationLog
from app.health_events.models.sleep_log import SleepLog
from app.health_events.models.stress_log import StressLog
from app.health_events.models.vitals_log import VitalsLog

_PERIOD_DAYS: dict[Period, int] = {"week": 7, "month": 30}

# Ordinal mapping so the sleep-quality enum can be averaged and charted as a
# line alongside hours slept — the same "dumb aggregation" treatment as every
# other numeric trend point, rather than a categorical breakdown that can't
# share an axis with the rest of the chart.
_SLEEP_QUALITY_SCORE: dict[SleepQuality, int] = {
    SleepQuality.poor: 1,
    SleepQuality.fair: 2,
    SleepQuality.good: 3,
    SleepQuality.excellent: 4,
}


def _normalize_glucose(value: float, from_unit: GlucoseUnit, to_unit: GlucoseUnit) -> float:
    if from_unit == to_unit:
        return value
    return mmol_l_to_mg_dl(value) if to_unit == GlucoseUnit.mg_dl else mg_dl_to_mmol_l(value)


def _date_range(period: Period) -> tuple[date, date, datetime, datetime]:
    days = _PERIOD_DAYS[period]
    today = datetime.now(UTC).date()
    start_date = today - timedelta(days=days - 1)
    range_start = datetime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    range_end = datetime(today.year, today.month, today.day, tzinfo=UTC) + timedelta(days=1)
    return start_date, today, range_start, range_end


def _days_in(start_date: date, today: date) -> list[date]:
    return [start_date + timedelta(days=offset) for offset in range((today - start_date).days + 1)]


async def _glucose_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
    unit: GlucoseUnit,
) -> list[DailyGlucoseTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp, GlucoseLog.value, GlucoseLog.unit)
        .join(GlucoseLog, GlucoseLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    values_by_day: dict[date, list[float]] = defaultdict(list)
    for event_timestamp, value, row_unit in result.all():
        values_by_day[event_timestamp.date()].append(_normalize_glucose(value, row_unit, unit))

    points: list[DailyGlucoseTrendPoint] = []
    for day in days:
        day_values = values_by_day.get(day, [])
        if day_values:
            points.append(
                DailyGlucoseTrendPoint(
                    date=day,
                    average=round(sum(day_values) / len(day_values), 1),
                    minimum=round(min(day_values), 1),
                    maximum=round(max(day_values), 1),
                    count=len(day_values),
                )
            )
        else:
            points.append(
                DailyGlucoseTrendPoint(date=day, average=None, minimum=None, maximum=None, count=0)
            )
    return points


async def _meal_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailyMealTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp, MealLog.estimated_carbs_g)
        .join(MealLog, MealLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    carbs_by_day: dict[date, list[float]] = defaultdict(list)
    counts_by_day: dict[date, int] = defaultdict(int)
    for event_timestamp, carbs in result.all():
        day = event_timestamp.date()
        counts_by_day[day] += 1
        if carbs is not None:
            carbs_by_day[day].append(carbs)

    points: list[DailyMealTrendPoint] = []
    for day in days:
        day_carbs = carbs_by_day.get(day, [])
        points.append(
            DailyMealTrendPoint(
                date=day,
                count=counts_by_day.get(day, 0),
                average_carbs_g=round(sum(day_carbs) / len(day_carbs), 1) if day_carbs else None,
            )
        )
    return points


async def _medication_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailyMedicationTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp, MedicationLog.taken)
        .join(MedicationLog, MedicationLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    taken_by_day: dict[date, int] = defaultdict(int)
    missed_by_day: dict[date, int] = defaultdict(int)
    for event_timestamp, taken in result.all():
        day = event_timestamp.date()
        if taken:
            taken_by_day[day] += 1
        else:
            missed_by_day[day] += 1

    points: list[DailyMedicationTrendPoint] = []
    for day in days:
        taken_count = taken_by_day.get(day, 0)
        missed_count = missed_by_day.get(day, 0)
        total = taken_count + missed_count
        points.append(
            DailyMedicationTrendPoint(
                date=day,
                taken_count=taken_count,
                missed_count=missed_count,
                adherence_pct=round(taken_count / total * 100, 1) if total else None,
            )
        )
    return points


async def _exercise_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailyExerciseTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp, ExerciseLog.duration_minutes)
        .join(ExerciseLog, ExerciseLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    minutes_by_day: dict[date, int] = defaultdict(int)
    counts_by_day: dict[date, int] = defaultdict(int)
    for event_timestamp, duration_minutes in result.all():
        day = event_timestamp.date()
        minutes_by_day[day] += duration_minutes
        counts_by_day[day] += 1

    return [
        DailyExerciseTrendPoint(
            date=day,
            total_minutes=minutes_by_day.get(day, 0),
            session_count=counts_by_day.get(day, 0),
        )
        for day in days
    ]


async def _sleep_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailySleepTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp, SleepLog.hours_slept, SleepLog.quality)
        .join(SleepLog, SleepLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    hours_by_day: dict[date, list[float]] = defaultdict(list)
    scores_by_day: dict[date, list[int]] = defaultdict(list)
    for event_timestamp, hours_slept, quality in result.all():
        day = event_timestamp.date()
        hours_by_day[day].append(hours_slept)
        scores_by_day[day].append(_SLEEP_QUALITY_SCORE[quality])

    points: list[DailySleepTrendPoint] = []
    for day in days:
        day_hours = hours_by_day.get(day, [])
        day_scores = scores_by_day.get(day, [])
        points.append(
            DailySleepTrendPoint(
                date=day,
                average_hours=round(sum(day_hours) / len(day_hours), 1) if day_hours else None,
                average_quality_score=round(sum(day_scores) / len(day_scores), 2)
                if day_scores
                else None,
            )
        )
    return points


async def _stress_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailyStressTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp, StressLog.stress_level, StressLog.energy_level)
        .join(StressLog, StressLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    stress_by_day: dict[date, list[int]] = defaultdict(list)
    energy_by_day: dict[date, list[int]] = defaultdict(list)
    for event_timestamp, stress_level, energy_level in result.all():
        day = event_timestamp.date()
        stress_by_day[day].append(stress_level)
        if energy_level is not None:
            energy_by_day[day].append(energy_level)

    points: list[DailyStressTrendPoint] = []
    for day in days:
        day_stress = stress_by_day.get(day, [])
        day_energy = energy_by_day.get(day, [])
        points.append(
            DailyStressTrendPoint(
                date=day,
                average_stress_level=round(sum(day_stress) / len(day_stress), 1)
                if day_stress
                else None,
                average_energy_level=round(sum(day_energy) / len(day_energy), 1)
                if day_energy
                else None,
            )
        )
    return points


async def _symptom_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailySymptomTrendPoint]:
    result = await db.execute(
        select(HealthEvent.event_timestamp).where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_type == EventType.symptom,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )
    counts_by_day: dict[date, int] = defaultdict(int)
    for (event_timestamp,) in result.all():
        counts_by_day[event_timestamp.date()] += 1

    return [DailySymptomTrendPoint(date=day, count=counts_by_day.get(day, 0)) for day in days]


async def _vitals_points(
    db: AsyncSession,
    patient_id: uuid.UUID,
    range_start: datetime,
    range_end: datetime,
    days: list[date],
) -> list[DailyVitalsTrendPoint]:
    # Weight and BP are independent point-in-time readings, not values to
    # average — each field just tracks the latest non-null value logged that
    # day, so a patient logging weight and BP in separate entries still gets
    # both reflected.
    result = await db.execute(
        select(
            HealthEvent.event_timestamp,
            VitalsLog.weight_kg,
            VitalsLog.blood_pressure_systolic,
            VitalsLog.blood_pressure_diastolic,
        )
        .join(VitalsLog, VitalsLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
        .order_by(HealthEvent.event_timestamp.asc())
    )
    weight_by_day: dict[date, float] = {}
    systolic_by_day: dict[date, int] = {}
    diastolic_by_day: dict[date, int] = {}
    for event_timestamp, weight_kg, systolic, diastolic in result.all():
        day = event_timestamp.date()
        if weight_kg is not None:
            weight_by_day[day] = weight_kg
        if systolic is not None:
            systolic_by_day[day] = systolic
        if diastolic is not None:
            diastolic_by_day[day] = diastolic

    return [
        DailyVitalsTrendPoint(
            date=day,
            latest_weight_kg=weight_by_day.get(day),
            latest_blood_pressure_systolic=systolic_by_day.get(day),
            latest_blood_pressure_diastolic=diastolic_by_day.get(day),
        )
        for day in days
    ]


async def get_trends(
    db: AsyncSession, patient_id: uuid.UUID, period: Period, glucose_unit: GlucoseUnit
) -> TrendsResponse:
    """Per-day rollups for all 8 event types over the trailing week or month,
    in one response so the frontend isn't making 8 separate calls. Every
    rollup is a dumb arithmetic aggregate (sum/avg/count) computed in Python
    after one bounded query per type — no pattern detection, that's Sprint 4.
    Every day in the range appears even with no events, so chart x-axes stay
    continuous instead of skipping gaps.
    """
    start_date, today, range_start, range_end = _date_range(period)
    days = _days_in(start_date, today)

    return TrendsResponse(
        period=period,
        start_date=start_date,
        end_date=today,
        glucose_unit=glucose_unit,
        glucose=await _glucose_points(db, patient_id, range_start, range_end, days, glucose_unit),
        meals=await _meal_points(db, patient_id, range_start, range_end, days),
        medication=await _medication_points(db, patient_id, range_start, range_end, days),
        exercise=await _exercise_points(db, patient_id, range_start, range_end, days),
        sleep=await _sleep_points(db, patient_id, range_start, range_end, days),
        stress=await _stress_points(db, patient_id, range_start, range_end, days),
        symptoms=await _symptom_points(db, patient_id, range_start, range_end, days),
        vitals=await _vitals_points(db, patient_id, range_start, range_end, days),
    )
