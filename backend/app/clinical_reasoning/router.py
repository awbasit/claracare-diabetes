from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.clinical_reasoning.schemas.assessment import ClinicalAssessment
from app.clinical_reasoning.services import clinical_reasoning_service
from app.database.session import get_db
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/context", tags=["clinical-context"])


@router.post("/snapshot", response_model=ClinicalAssessment, status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> ClinicalAssessment:
    return await clinical_reasoning_service.generate_assessment(db, patient.id)


@router.get("/snapshot/latest", response_model=ClinicalAssessment)
async def get_latest_snapshot(
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> ClinicalAssessment:
    assessment = await clinical_reasoning_service.get_latest_snapshot(db, patient.id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No context snapshot found for this patient",
        )
    return assessment


@router.get("/snapshot/{version}", response_model=ClinicalAssessment)
async def get_snapshot_by_version(
    version: int,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> ClinicalAssessment:
    assessment = await clinical_reasoning_service.get_snapshot_by_version(db, patient.id, version)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No context snapshot version {version} found for this patient",
        )
    return assessment
