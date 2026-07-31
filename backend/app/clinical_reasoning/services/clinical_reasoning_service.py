import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.models.patient_context_snapshot import PatientContextSnapshot
from app.clinical_reasoning.schemas.assessment import ClinicalAssessment
from app.clinical_reasoning.schemas.findings import MissingInformation
from app.clinical_reasoning.services import context_service
from app.clinical_reasoning.services.confidence_calculators import run_all_calculators
from app.clinical_reasoning.services.rules import RuleRegistry

_rule_registry = RuleRegistry()


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
