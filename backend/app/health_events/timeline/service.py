import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.glucose.service import mmol_l_to_mg_dl
from app.health_events.models.enums import EventType, GlucoseUnit
from app.health_events.models.exercise_log import ExerciseLog
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.medication_log import MedicationLog
from app.health_events.models.stress_log import StressLog
from app.health_events.timeline.schemas import DailySummary, build_glucose_detail

# "Same day" is interpreted as a UTC calendar day — the system has no
# per-patient timezone stored yet, and all event_timestamps are UTC.


async def get_daily_summary(
    db: AsyncSession, patient_id: uuid.UUID, target_date: date
) -> DailySummary:
    day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=UTC)
    day_end = day_start + timedelta(days=1)

    counts_result = await db.execute(
        select(HealthEvent.event_type, func.count())
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= day_start,
            HealthEvent.event_timestamp < day_end,
        )
        .group_by(HealthEvent.event_type)
    )
    event_counts = dict.fromkeys(EventType, 0)
    for event_type, count in counts_result.all():
        event_counts[event_type] = count
    total_events = sum(event_counts.values())

    medication_result = await db.execute(
        select(MedicationLog.taken, func.count())
        .join(HealthEvent, HealthEvent.id == MedicationLog.health_event_id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= day_start,
            HealthEvent.event_timestamp < day_end,
        )
        .group_by(MedicationLog.taken)
    )
    taken_counts: dict[bool, int] = {taken: count for taken, count in medication_result.all()}
    medications_taken = taken_counts.get(True, 0)
    medications_missed = taken_counts.get(False, 0)

    # One query covers both "latest reading" and "today's average" — no need
    # to hit glucose_logs twice.
    glucose_result = await db.execute(
        select(HealthEvent.event_timestamp, GlucoseLog)
        .join(GlucoseLog, GlucoseLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= day_start,
            HealthEvent.event_timestamp < day_end,
        )
        .order_by(HealthEvent.event_timestamp.desc())
    )
    glucose_rows = glucose_result.all()
    latest_glucose = None
    latest_glucose_timestamp = None
    glucose_average_mg_dl = None
    if glucose_rows:
        latest_timestamp, latest_log = glucose_rows[0]
        latest_glucose_timestamp = latest_timestamp
        latest_glucose = build_glucose_detail(latest_log)
        mg_dl_values = [
            log.value if log.unit == GlucoseUnit.mg_dl else mmol_l_to_mg_dl(log.value)
            for _, log in glucose_rows
        ]
        glucose_average_mg_dl = round(sum(mg_dl_values) / len(mg_dl_values), 1)

    exercise_result = await db.execute(
        select(func.coalesce(func.sum(ExerciseLog.duration_minutes), 0))
        .join(HealthEvent, HealthEvent.id == ExerciseLog.health_event_id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= day_start,
            HealthEvent.event_timestamp < day_end,
        )
    )
    total_exercise_minutes = exercise_result.scalar_one()

    stress_result = await db.execute(
        select(func.avg(StressLog.stress_level))
        .join(HealthEvent, HealthEvent.id == StressLog.health_event_id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= day_start,
            HealthEvent.event_timestamp < day_end,
        )
    )
    avg_stress = stress_result.scalar_one()
    average_stress_level = round(float(avg_stress), 1) if avg_stress is not None else None

    return DailySummary(
        date=target_date,
        event_counts=event_counts,
        total_events=total_events,
        medications_taken=medications_taken,
        medications_missed=medications_missed,
        latest_glucose=latest_glucose,
        latest_glucose_timestamp=latest_glucose_timestamp,
        glucose_average_mg_dl=glucose_average_mg_dl,
        total_exercise_minutes=total_exercise_minutes,
        average_stress_level=average_stress_level,
    )
