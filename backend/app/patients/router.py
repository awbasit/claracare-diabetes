import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.models.medication import Medication
from app.models.patient import Patient
from app.patients import service
from app.patients.schemas import BaselineAssessmentSubmit, PatientProfileRead
from app.schemas.baseline_assessment import BaselineAssessmentRead
from app.schemas.lifestyle_profile import LifestyleProfileRead, LifestyleProfileUpdate
from app.schemas.medical_history import MedicalHistoryRead, MedicalHistoryUpdate
from app.schemas.medication import MedicationBase, MedicationRead, MedicationUpdate
from app.schemas.patient import PatientRead, PatientUpdate

router = APIRouter(prefix="/api/patients/me", tags=["patients"])


async def _get_owned_medication_or_404(
    db: AsyncSession, patient: Patient, medication_id: uuid.UUID
) -> Medication:
    medication = await service.get_own_medication(db, patient.id, medication_id)
    if medication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return medication


@router.get("/profile", response_model=PatientProfileRead)
async def get_profile(
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> PatientProfileRead:
    medical_history = await service.get_medical_history(db, patient.id)
    lifestyle_profile = await service.get_lifestyle_profile(db, patient.id)
    medications = await service.list_medications(db, patient.id, active_only=True)
    return PatientProfileRead(
        patient=PatientRead.model_validate(patient),
        medical_history=MedicalHistoryRead.model_validate(medical_history) if medical_history else None,
        lifestyle_profile=(
            LifestyleProfileRead.model_validate(lifestyle_profile) if lifestyle_profile else None
        ),
        medications=[MedicationRead.model_validate(m) for m in medications],
    )


@router.put("/profile", response_model=PatientRead)
async def update_profile(
    payload: PatientUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> PatientRead:
    updated = await service.update_patient(db, patient, payload.model_dump(exclude_unset=True))
    return PatientRead.model_validate(updated)


@router.put("/medical-history", response_model=MedicalHistoryRead)
async def upsert_medical_history(
    payload: MedicalHistoryUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> MedicalHistoryRead:
    history = await service.upsert_medical_history(db, patient.id, payload.model_dump(exclude_unset=True))
    return MedicalHistoryRead.model_validate(history)


@router.put("/lifestyle", response_model=LifestyleProfileRead)
async def upsert_lifestyle(
    payload: LifestyleProfileUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> LifestyleProfileRead:
    profile = await service.upsert_lifestyle_profile(
        db, patient.id, payload.model_dump(exclude_unset=True)
    )
    return LifestyleProfileRead.model_validate(profile)


@router.get("/medications", response_model=list[MedicationRead])
async def list_medications(
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[MedicationRead]:
    medications = await service.list_medications(db, patient.id)
    return [MedicationRead.model_validate(m) for m in medications]


@router.post("/medications", response_model=MedicationRead, status_code=status.HTTP_201_CREATED)
async def create_medication(
    payload: MedicationBase,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> MedicationRead:
    medication = await service.create_medication(db, patient.id, payload.model_dump())
    return MedicationRead.model_validate(medication)


@router.put("/medications/{medication_id}", response_model=MedicationRead)
async def update_medication(
    medication_id: uuid.UUID,
    payload: MedicationUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> MedicationRead:
    medication = await _get_owned_medication_or_404(db, patient, medication_id)
    updated = await service.update_medication(db, medication, payload.model_dump(exclude_unset=True))
    return MedicationRead.model_validate(updated)


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> None:
    medication = await _get_owned_medication_or_404(db, patient, medication_id)
    await service.deactivate_medication(db, medication)


@router.post(
    "/baseline-assessment", response_model=BaselineAssessmentRead, status_code=status.HTTP_201_CREATED
)
async def submit_baseline_assessment(
    payload: BaselineAssessmentSubmit,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> BaselineAssessmentRead:
    assessment = await service.submit_baseline_assessment(
        db, patient.id, payload.notes, payload.raw_answers
    )
    return BaselineAssessmentRead.model_validate(assessment)
