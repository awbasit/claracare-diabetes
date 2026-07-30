import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.baseline_assessment import BaselineAssessment
from app.models.lifestyle_profile import LifestyleProfile
from app.models.medical_history import MedicalHistory
from app.models.medication import Medication
from app.models.patient import Patient


def compute_bmi(height_cm: float | None, weight_kg: float | None) -> float | None:
    if not height_cm or not weight_kg:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m**2), 1)


async def update_patient(db: AsyncSession, patient: Patient, updates: dict[str, Any]) -> Patient:
    for field, value in updates.items():
        setattr(patient, field, value)
    patient.bmi = compute_bmi(patient.height_cm, patient.weight_kg)
    await db.commit()
    await db.refresh(patient)
    return patient


async def get_medical_history(db: AsyncSession, patient_id: uuid.UUID) -> MedicalHistory | None:
    result = await db.execute(select(MedicalHistory).where(MedicalHistory.patient_id == patient_id))
    return result.scalar_one_or_none()


async def upsert_medical_history(
    db: AsyncSession, patient_id: uuid.UUID, updates: dict[str, Any]
) -> MedicalHistory:
    history = await get_medical_history(db, patient_id)
    if history is None:
        history = MedicalHistory(patient_id=patient_id, **updates)
        db.add(history)
    else:
        for field, value in updates.items():
            setattr(history, field, value)
    await db.commit()
    await db.refresh(history)
    return history


async def get_lifestyle_profile(db: AsyncSession, patient_id: uuid.UUID) -> LifestyleProfile | None:
    result = await db.execute(select(LifestyleProfile).where(LifestyleProfile.patient_id == patient_id))
    return result.scalar_one_or_none()


async def upsert_lifestyle_profile(
    db: AsyncSession, patient_id: uuid.UUID, updates: dict[str, Any]
) -> LifestyleProfile:
    profile = await get_lifestyle_profile(db, patient_id)
    if profile is None:
        profile = LifestyleProfile(patient_id=patient_id, **updates)
        db.add(profile)
    else:
        for field, value in updates.items():
            setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile


async def list_medications(
    db: AsyncSession, patient_id: uuid.UUID, *, active_only: bool = False
) -> list[Medication]:
    stmt = select(Medication).where(Medication.patient_id == patient_id)
    if active_only:
        stmt = stmt.where(Medication.is_active.is_(True))
    stmt = stmt.order_by(Medication.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_own_medication(
    db: AsyncSession, patient_id: uuid.UUID, medication_id: uuid.UUID
) -> Medication | None:
    result = await db.execute(
        select(Medication).where(Medication.id == medication_id, Medication.patient_id == patient_id)
    )
    return result.scalar_one_or_none()


async def create_medication(db: AsyncSession, patient_id: uuid.UUID, data: dict[str, Any]) -> Medication:
    medication = Medication(patient_id=patient_id, **data)
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def update_medication(
    db: AsyncSession, medication: Medication, updates: dict[str, Any]
) -> Medication:
    for field, value in updates.items():
        setattr(medication, field, value)
    await db.commit()
    await db.refresh(medication)
    return medication


async def deactivate_medication(db: AsyncSession, medication: Medication) -> Medication:
    medication.is_active = False
    await db.commit()
    await db.refresh(medication)
    return medication


async def get_baseline_assessment(db: AsyncSession, patient_id: uuid.UUID) -> BaselineAssessment | None:
    result = await db.execute(
        select(BaselineAssessment).where(BaselineAssessment.patient_id == patient_id)
    )
    return result.scalar_one_or_none()


async def submit_baseline_assessment(
    db: AsyncSession, patient_id: uuid.UUID, notes: str | None, raw_answers: dict[str, Any]
) -> BaselineAssessment:
    assessment = await get_baseline_assessment(db, patient_id)
    completed_at = datetime.now(timezone.utc)
    if assessment is None:
        assessment = BaselineAssessment(
            patient_id=patient_id, notes=notes, raw_answers=raw_answers, completed_at=completed_at
        )
        db.add(assessment)
    else:
        assessment.notes = notes
        assessment.raw_answers = raw_answers
        assessment.completed_at = completed_at
    await db.commit()
    await db.refresh(assessment)
    return assessment
