from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.analytics import service as analytics_service
from app.health_events.analytics.schemas import GlucoseTrendResponse, Period
from app.health_events.models.enums import GlucoseUnit
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/analytics", tags=["analytics"])


@router.get("/glucose-trend", response_model=GlucoseTrendResponse)
async def get_glucose_trend(
    period: Period = Query("week"),
    unit: GlucoseUnit = Query(GlucoseUnit.mg_dl),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> GlucoseTrendResponse:
    return await analytics_service.get_glucose_trend(db, patient.id, period, unit)
