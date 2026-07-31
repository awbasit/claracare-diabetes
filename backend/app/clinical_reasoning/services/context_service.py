import statistics
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.models.enums import PatientGoalStatus
from app.clinical_reasoning.models.patient_context_snapshot import PatientContextSnapshot
from app.clinical_reasoning.models.patient_goal import PatientGoal as PatientGoalModel
from app.clinical_reasoning.schemas.context import (
    AdherenceSummary,
    DemographicsSummary,
    DiabetesHistorySummary,
    GlucoseReading,
    LifestyleSummary,
    MedicationSummary,
    PatientContext,
    PatientGoal,
    SymptomSummary,
    TimelineSummary,
)
from app.health_events.analytics import service as analytics_service
from app.health_events.glucose.service import mmol_l_to_mg_dl
from app.health_events.models.enums import EventType, GlucoseUnit
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.medication_log import MedicationLog
from app.health_events.services import health_event_service
from app.health_events.timeline import service as timeline_service
from app.health_events.timeline.schemas import build_glucose_detail
from app.models.lifestyle_profile import LifestyleProfile
from app.models.medical_history import MedicalHistory
from app.models.patient import Patient
from app.patients import service as patients_service

# How far back an active symptom can have been logged and still count as
# "active" context for e.g. an interview agent — not a clinical definition,
# just a documented recency window.
_ACTIVE_SYMPTOM_WINDOW_DAYS = 3


def _build_demographics(patient: Patient) -> DemographicsSummary:
    return DemographicsSummary(
        age=patient.age,
        sex=patient.sex,
        height_cm=patient.height_cm,
        weight_kg=patient.weight_kg,
        bmi=patient.bmi,
        occupation=patient.occupation,
        work_schedule=patient.work_schedule,
    )


def _build_diabetes_history(history: MedicalHistory | None) -> DiabetesHistorySummary:
    if history is None:
        return DiabetesHistorySummary(
            diabetes_type=None,
            years_since_diagnosis=None,
            family_history=False,
            family_history_notes=None,
            latest_hba1c=None,
            latest_blood_pressure_systolic=None,
            latest_blood_pressure_diastolic=None,
            latest_cholesterol=None,
            has_kidney_disease=False,
            has_eye_disease=False,
            has_neuropathy=False,
            comorbidities=[],
        )
    return DiabetesHistorySummary(
        diabetes_type=history.diabetes_type,
        years_since_diagnosis=history.years_since_diagnosis,
        family_history=history.family_history,
        family_history_notes=history.family_history_notes,
        latest_hba1c=history.latest_hba1c,
        latest_blood_pressure_systolic=history.latest_blood_pressure_systolic,
        latest_blood_pressure_diastolic=history.latest_blood_pressure_diastolic,
        latest_cholesterol=history.latest_cholesterol,
        has_kidney_disease=history.has_kidney_disease,
        has_eye_disease=history.has_eye_disease,
        has_neuropathy=history.has_neuropathy,
        comorbidities=list(history.comorbidities),
    )


def _build_lifestyle(profile: LifestyleProfile | None) -> LifestyleSummary:
    if profile is None:
        return LifestyleSummary(
            sleep_hours_avg=None,
            exercise_frequency=None,
            exercise_type=None,
            smoking_status=None,
            alcohol_use=None,
            stress_level_baseline=None,
            meal_schedule_notes=None,
        )
    return LifestyleSummary(
        sleep_hours_avg=profile.sleep_hours_avg,
        exercise_frequency=profile.exercise_frequency,
        exercise_type=profile.exercise_type,
        smoking_status=profile.smoking_status,
        alcohol_use=profile.alcohol_use,
        stress_level_baseline=profile.stress_level_baseline,
        meal_schedule_notes=profile.meal_schedule_notes,
    )


async def _build_medications(db: AsyncSession, patient_id: uuid.UUID) -> list[MedicationSummary]:
    medications = await patients_service.list_medications(db, patient_id, active_only=True)

    last_logged_result = await db.execute(
        select(MedicationLog.medication_id, func.max(HealthEvent.event_timestamp))
        .join(HealthEvent, HealthEvent.id == MedicationLog.health_event_id)
        .where(HealthEvent.patient_id == patient_id)
        .group_by(MedicationLog.medication_id)
    )
    last_logged_by_id: dict[uuid.UUID, datetime] = {
        medication_id: last_logged for medication_id, last_logged in last_logged_result.all()
    }

    return [
        MedicationSummary(
            id=medication.id,
            name=medication.name,
            dosage=medication.dosage,
            frequency=medication.frequency,
            time_of_day=medication.time_of_day,
            purpose=medication.purpose,
            is_active=medication.is_active,
            last_logged_at=last_logged_by_id.get(medication.id),
        )
        for medication in medications
    ]


async def _build_latest_glucose(db: AsyncSession, patient_id: uuid.UUID) -> GlucoseReading | None:
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.glucose], limit=1
    )
    if not events:
        return None
    event, detail = events[0]
    reading = build_glucose_detail(detail)
    return GlucoseReading(
        value=reading.value,
        unit=reading.unit,
        reading_type=reading.reading_type,
        timestamp=event.event_timestamp,
    )


async def _build_timeline_summary(
    db: AsyncSession, patient_id: uuid.UUID, now: datetime
) -> tuple[TimelineSummary, AdherenceSummary]:
    # Window runs through the end of today (matching analytics_service's own
    # day-boundary convention), not the exact current instant — otherwise an
    # event logged later today than "now" would be silently excluded here
    # while still showing up via analytics_service's trend endpoints.
    end_of_today = datetime(now.year, now.month, now.day, tzinfo=UTC) + timedelta(days=1)
    week_ago = end_of_today - timedelta(days=7)

    # Raw glucose readings for the week — fetched directly (not via the
    # analytics trend endpoint) because stdev needs the individual values,
    # which the day-bucketed trend response doesn't expose.
    glucose_events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.glucose], start=week_ago, end=end_of_today, limit=500
    )
    glucose_mg_dl_values = [
        detail.value if detail.unit == GlucoseUnit.mg_dl else mmol_l_to_mg_dl(detail.value)
        for _, detail in glucose_events
    ]
    glucose_average = (
        round(sum(glucose_mg_dl_values) / len(glucose_mg_dl_values), 1)
        if glucose_mg_dl_values
        else None
    )
    glucose_stdev = (
        round(statistics.pstdev(glucose_mg_dl_values), 1)
        if len(glucose_mg_dl_values) >= 2
        else None
    )

    last_meal_events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.meal], limit=1
    )
    last_meal_at = last_meal_events[0][0].event_timestamp if last_meal_events else None

    last_sleep_events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.sleep], limit=1
    )
    last_sleep_at = last_sleep_events[0][0].event_timestamp if last_sleep_events else None

    trends = await analytics_service.get_trends(db, patient_id, "week", GlucoseUnit.mg_dl)
    daily_summary = await timeline_service.get_daily_summary(db, patient_id, now.date())

    meals_logged_count = sum(point.count for point in trends.meals)
    exercise_total_minutes = sum(point.total_minutes for point in trends.exercise)
    exercise_session_count = sum(point.session_count for point in trends.exercise)
    symptoms_logged_count = sum(point.count for point in trends.symptoms)

    sleep_hour_values = [
        point.average_hours for point in trends.sleep if point.average_hours is not None
    ]
    sleep_average_hours = (
        round(sum(sleep_hour_values) / len(sleep_hour_values), 1) if sleep_hour_values else None
    )

    stress_values = [
        point.average_stress_level
        for point in trends.stress
        if point.average_stress_level is not None
    ]
    average_stress_level = (
        round(sum(stress_values) / len(stress_values), 1) if stress_values else None
    )

    doses_taken_7day = sum(point.taken_count for point in trends.medication)
    doses_missed_7day = sum(point.missed_count for point in trends.medication)

    # A partial rollup by design — sleep/vitals trend points track latest
    # values, not per-day counts, so they aren't included here.
    total_events = (
        len(glucose_events)
        + meals_logged_count
        + doses_taken_7day
        + doses_missed_7day
        + exercise_session_count
        + symptoms_logged_count
    )

    timeline_summary = TimelineSummary(
        period_days=7,
        total_events=total_events,
        glucose_reading_count=len(glucose_events),
        glucose_average_mg_dl=glucose_average,
        glucose_stdev_mg_dl=glucose_stdev,
        meals_logged_count=meals_logged_count,
        meals_logged_today=daily_summary.event_counts.get(EventType.meal, 0),
        last_meal_at=last_meal_at,
        exercise_total_minutes=exercise_total_minutes,
        exercise_session_count=exercise_session_count,
        sleep_average_hours=sleep_average_hours,
        last_sleep_at=last_sleep_at,
        average_stress_level=average_stress_level,
        symptoms_logged_count=symptoms_logged_count,
    )
    total_doses = doses_taken_7day + doses_missed_7day
    adherence_summary = AdherenceSummary(
        doses_taken_7day=doses_taken_7day,
        doses_missed_7day=doses_missed_7day,
        adherence_pct_7day=round(doses_taken_7day / total_doses * 100, 1)
        if total_doses > 0
        else None,
    )
    return timeline_summary, adherence_summary


async def _build_active_symptoms(
    db: AsyncSession, patient_id: uuid.UUID, now: datetime
) -> list[SymptomSummary]:
    # Same end-of-today boundary as _build_timeline_summary, for the same
    # reason — a symptom logged later today than "now" must still count.
    end_of_today = datetime(now.year, now.month, now.day, tzinfo=UTC) + timedelta(days=1)
    window_start = end_of_today - timedelta(days=_ACTIVE_SYMPTOM_WINDOW_DAYS)
    events = await health_event_service.get_events(
        db,
        patient_id,
        event_types=[EventType.symptom],
        start=window_start,
        end=end_of_today,
        limit=50,
    )
    return [
        SymptomSummary(
            symptom_type=detail.symptom_type,
            severity=detail.severity,
            logged_at=event.event_timestamp,
            duration_notes=detail.duration_notes,
        )
        for event, detail in events
    ]


async def _build_goals(db: AsyncSession, patient_id: uuid.UUID) -> list[PatientGoal]:
    result = await db.execute(
        select(PatientGoalModel)
        .where(
            PatientGoalModel.patient_id == patient_id,
            PatientGoalModel.status == PatientGoalStatus.active,
        )
        .order_by(PatientGoalModel.set_at.desc())
    )
    return [
        PatientGoal(
            id=goal.id,
            goal=goal.goal,
            context=goal.context,
            status=goal.status.value,
            set_at=goal.set_at,
            source=goal.source.value,
        )
        for goal in result.scalars().all()
    ]


async def _next_version(db: AsyncSession, patient_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.max(PatientContextSnapshot.version)).where(
            PatientContextSnapshot.patient_id == patient_id
        )
    )
    max_version = result.scalar_one_or_none()
    return (max_version or 0) + 1


async def build_context(db: AsyncSession, patient_id: uuid.UUID) -> PatientContext:
    """Assembles a fresh, versioned PatientContext. Does NOT persist —
    persistence happens once, in the Clinical Reasoning Service, after the
    full ClinicalAssessment built from this context is ready, so a context
    and its assessment are always saved together.
    """
    now = datetime.now(UTC)

    patient_result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = patient_result.scalar_one()

    medical_history = await patients_service.get_medical_history(db, patient_id)
    lifestyle_profile = await patients_service.get_lifestyle_profile(db, patient_id)

    medications = await _build_medications(db, patient_id)
    latest_glucose = await _build_latest_glucose(db, patient_id)
    timeline_summary, adherence_summary = await _build_timeline_summary(db, patient_id, now)
    active_symptoms = await _build_active_symptoms(db, patient_id, now)
    goals = await _build_goals(db, patient_id)
    version = await _next_version(db, patient_id)

    return PatientContext(
        patient_id=patient_id,
        version=version,
        generated_at=now,
        demographics=_build_demographics(patient),
        diabetes_history=_build_diabetes_history(medical_history),
        medications=medications,
        latest_glucose=latest_glucose,
        last_7_day_summary=timeline_summary,
        adherence_summary=adherence_summary,
        active_symptoms=active_symptoms,
        lifestyle_summary=_build_lifestyle(lifestyle_profile),
        goals=goals,
        recent_patterns=[],
        known_barriers=[],
    )
