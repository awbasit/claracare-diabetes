import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.models.patient_context_snapshot import PatientContextSnapshot
from app.clinical_reasoning.schemas.assessment import ClinicalAssessment
from app.clinical_reasoning.schemas.context import GlucoseReading, SymptomSummary
from app.clinical_reasoning.schemas.findings import MissingInformation
from app.clinical_reasoning.schemas.live_queries import (
    LatestVitalsSummary,
    MealEntry,
    MedicationAdherenceSummary,
    RecentMealsSummary,
    RecentSymptomsSummary,
    SleepSummary,
    TodayGlucoseSummary,
)
from app.clinical_reasoning.services import context_service
from app.clinical_reasoning.services.confidence_calculators import run_all_calculators
from app.clinical_reasoning.services.rules import RuleRegistry
from app.health_events.glucose.service import mmol_l_to_mg_dl
from app.health_events.models.enums import EventType, GlucoseUnit, SleepQuality
from app.health_events.services import health_event_service

_rule_registry = RuleRegistry()

# Same ordinal treatment as analytics/service.py's own _SLEEP_QUALITY_SCORE —
# duplicated rather than imported since that one is a private module-level
# constant of an unrelated service, and the mapping is three lines.
_SLEEP_QUALITY_SCORE: dict[SleepQuality, int] = {
    SleepQuality.poor: 1,
    SleepQuality.fair: 2,
    SleepQuality.good: 3,
    SleepQuality.excellent: 4,
}


def _derive_uncertainties(missing_information: list[MissingInformation]) -> list[str]:
    # Deterministic, not LLM-derived: a "not enough info" note for each
    # high-severity gap the rules engine already found. Low/medium-severity
    # gaps are surfaced via missing_information alone.
    return [
        f"Not enough recent {item.event_type} data to assess confidently: {item.reason}"
        for item in missing_information
        if item.severity == "high"
    ]


async def generate_assessment(db: AsyncSession, patient_id: uuid.UUID) -> ClinicalAssessment:
    """The only entry point Milestone 3.2's Clinical Tool Layer calls.
    Orchestrates Context Service -> Rules -> Confidence Calculators into one
    ClinicalAssessment, then persists exactly one snapshot row containing
    both the context and the assessment, at the version the Context Service
    assigned — so a context and its assessment are always saved together.
    """
    context = await context_service.build_context(db, patient_id)
    missing_information = _rule_registry.evaluate(context)
    data_quality = await run_all_calculators(db, patient_id)

    assessment = ClinicalAssessment(
        version=context.version,
        context_version=context.version,
        generated_at=datetime.now(UTC),
        patient_context=context,
        data_quality=data_quality,
        contradictions=[],  # nothing produces these yet — Milestone 3.2
        missing_information=missing_information,
        uncertainties=_derive_uncertainties(missing_information),
    )

    snapshot = PatientContextSnapshot(
        patient_id=patient_id,
        version=context.version,
        context=context.model_dump(mode="json"),
        assessment=assessment.model_dump(mode="json"),
    )
    db.add(snapshot)
    await db.commit()

    return assessment


async def get_latest_snapshot(db: AsyncSession, patient_id: uuid.UUID) -> ClinicalAssessment | None:
    result = await db.execute(
        select(PatientContextSnapshot)
        .where(PatientContextSnapshot.patient_id == patient_id)
        .order_by(PatientContextSnapshot.version.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if snapshot is None:
        return None
    return ClinicalAssessment.model_validate(snapshot.assessment)


async def get_snapshot_by_version(
    db: AsyncSession, patient_id: uuid.UUID, version: int
) -> ClinicalAssessment | None:
    result = await db.execute(
        select(PatientContextSnapshot).where(
            PatientContextSnapshot.patient_id == patient_id,
            PatientContextSnapshot.version == version,
        )
    )
    snapshot = result.scalar_one_or_none()
    if snapshot is None:
        return None
    return ClinicalAssessment.model_validate(snapshot.assessment)


# --- Live queries (Milestone 3.2 Clinical Tool Layer) ----------------------
# Unlike generate_assessment/get_latest_snapshot above, these always hit
# HealthEvent directly and never read/write PatientContextSnapshot — the
# whole point is to answer "what's true right now", for an in-progress
# interview where even a just-generated snapshot may already be a few
# minutes stale relative to what the patient is telling the agent this turn.


def _day_bounds(now: datetime, days: int) -> tuple[datetime, datetime]:
    end = datetime(now.year, now.month, now.day, tzinfo=UTC) + timedelta(days=1)
    start = end - timedelta(days=days)
    return start, end


async def get_today_glucose(db: AsyncSession, patient_id: uuid.UUID) -> TodayGlucoseSummary:
    start, end = _day_bounds(datetime.now(UTC), 1)
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.glucose], start=start, end=end, limit=100
    )
    readings = [
        GlucoseReading(
            value=detail.value,
            unit=detail.unit,
            reading_type=detail.reading_type,
            timestamp=event.event_timestamp,
        )
        for event, detail in events
    ]
    mg_dl_values = [
        reading.value if reading.unit == GlucoseUnit.mg_dl else mmol_l_to_mg_dl(reading.value)
        for reading in readings
    ]
    average = round(sum(mg_dl_values) / len(mg_dl_values), 1) if mg_dl_values else None
    return TodayGlucoseSummary(readings=readings, count=len(readings), average_mg_dl=average)


async def get_recent_meals(
    db: AsyncSession, patient_id: uuid.UUID, days: int = 3
) -> RecentMealsSummary:
    start, end = _day_bounds(datetime.now(UTC), days)
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.meal], start=start, end=end, limit=200
    )
    meals = [
        MealEntry(
            meal_type=detail.meal_type,
            food_items=detail.food_items,
            estimated_carbs_g=detail.estimated_carbs_g,
            timestamp=event.event_timestamp,
        )
        for event, detail in events
    ]
    return RecentMealsSummary(period_days=days, meals=meals, count=len(meals))


async def get_medication_adherence(
    db: AsyncSession, patient_id: uuid.UUID, days: int = 7
) -> MedicationAdherenceSummary:
    start, end = _day_bounds(datetime.now(UTC), days)
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.medication], start=start, end=end, limit=500
    )
    doses_taken = sum(1 for _, detail in events if detail.taken)
    doses_missed = len(events) - doses_taken
    total = doses_taken + doses_missed
    adherence_pct = round(doses_taken / total * 100, 1) if total > 0 else None
    return MedicationAdherenceSummary(
        period_days=days,
        doses_taken=doses_taken,
        doses_missed=doses_missed,
        adherence_pct=adherence_pct,
    )


async def get_sleep_summary(db: AsyncSession, patient_id: uuid.UUID, days: int = 7) -> SleepSummary:
    start, end = _day_bounds(datetime.now(UTC), days)
    # get_events orders newest-first, so events[0] (if any) is last night's.
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.sleep], start=start, end=end, limit=200
    )
    hours = [detail.hours_slept for _, detail in events]
    quality_scores = [_SLEEP_QUALITY_SCORE[detail.quality] for _, detail in events]
    return SleepSummary(
        period_days=days,
        nights_logged=len(events),
        average_hours=round(sum(hours) / len(hours), 1) if hours else None,
        last_night_hours=events[0][1].hours_slept if events else None,
        average_quality_score=round(sum(quality_scores) / len(quality_scores), 2)
        if quality_scores
        else None,
    )


async def get_latest_vitals(db: AsyncSession, patient_id: uuid.UUID) -> LatestVitalsSummary | None:
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.vitals], limit=1
    )
    if not events:
        return None
    event, detail = events[0]
    return LatestVitalsSummary(
        weight_kg=detail.weight_kg,
        blood_pressure_systolic=detail.blood_pressure_systolic,
        blood_pressure_diastolic=detail.blood_pressure_diastolic,
        heart_rate=detail.heart_rate,
        logged_at=event.event_timestamp,
    )


async def get_recent_symptoms(
    db: AsyncSession, patient_id: uuid.UUID, days: int = 7
) -> RecentSymptomsSummary:
    start, end = _day_bounds(datetime.now(UTC), days)
    events = await health_event_service.get_events(
        db, patient_id, event_types=[EventType.symptom], start=start, end=end, limit=200
    )
    symptoms = [
        SymptomSummary(
            symptom_type=detail.symptom_type,
            severity=detail.severity,
            logged_at=event.event_timestamp,
            duration_notes=detail.duration_notes,
        )
        for event, detail in events
    ]
    return RecentSymptomsSummary(period_days=days, symptoms=symptoms, count=len(symptoms))
