import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent
from app.health_events.services import health_event_service
from app.health_events.stress.schemas import StressLogCreate, StressLogRead, StressLogUpdate
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/stress", tags=["stress"])

_DETAIL_FIELDS = ("stress_level", "mood", "energy_level")


async def _get_owned_stress_event_or_404(
    db: AsyncSession, patient: Patient, event_id: uuid.UUID
) -> HealthEvent:
    event = await health_event_service.get_own_event_of_type(
        db, patient.id, event_id, EventType.stress
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stress log not found")
    return event


@router.post("", response_model=StressLogRead, status_code=status.HTTP_201_CREATED)
async def create_stress_log(
    payload: StressLogCreate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> StressLogRead:
    event, detail = await health_event_service.create_event(
        db,
        patient_id=patient.id,
        event_type=EventType.stress,
        event_timestamp=payload.event_timestamp,
        notes=payload.notes,
        detail_data={
            "stress_level": payload.stress_level,
            "mood": payload.mood,
            "energy_level": payload.energy_level,
        },
    )
    return StressLogRead.from_event_and_detail(event, detail)


@router.get("", response_model=list[StressLogRead])
async def list_stress_logs(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[StressLogRead]:
    events = await health_event_service.get_events(
        db,
        patient.id,
        event_type=EventType.stress,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return [StressLogRead.from_event_and_detail(event, detail) for event, detail in events]


@router.get("/{event_id}", response_model=StressLogRead)
async def get_stress_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> StressLogRead:
    event = await _get_owned_stress_event_or_404(db, patient, event_id)
    detail = await health_event_service.get_event_detail(db, event)
    return StressLogRead.from_event_and_detail(event, detail)


@router.put("/{event_id}", response_model=StressLogRead)
async def update_stress_log(
    event_id: uuid.UUID,
    payload: StressLogUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> StressLogRead:
    event = await _get_owned_stress_event_or_404(db, patient, event_id)

    updates = payload.model_dump(exclude_unset=True)
    event_updates = {key: updates[key] for key in ("event_timestamp", "notes") if key in updates}
    detail_updates = {key: updates[key] for key in _DETAIL_FIELDS if key in updates}

    updated_event, updated_detail = await health_event_service.update_event(
        db, event, event_updates=event_updates, detail_updates=detail_updates
    )
    return StressLogRead.from_event_and_detail(updated_event, updated_detail)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stress_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> None:
    event = await _get_owned_stress_event_or_404(db, patient, event_id)
    await health_event_service.delete_event(db, event)
