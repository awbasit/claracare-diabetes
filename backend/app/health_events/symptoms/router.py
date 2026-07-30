import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent
from app.health_events.services import health_event_service
from app.health_events.symptoms.schemas import SymptomLogCreate, SymptomLogRead, SymptomLogUpdate
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/symptoms", tags=["symptoms"])

_DETAIL_FIELDS = ("symptom_type", "severity", "duration_notes")


async def _get_owned_symptom_event_or_404(
    db: AsyncSession, patient: Patient, event_id: uuid.UUID
) -> HealthEvent:
    event = await health_event_service.get_own_event_of_type(
        db, patient.id, event_id, EventType.symptom
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom log not found")
    return event


@router.post("", response_model=SymptomLogRead, status_code=status.HTTP_201_CREATED)
async def create_symptom_log(
    payload: SymptomLogCreate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> SymptomLogRead:
    event, detail = await health_event_service.create_event(
        db,
        patient_id=patient.id,
        event_type=EventType.symptom,
        event_timestamp=payload.event_timestamp,
        notes=payload.notes,
        detail_data={
            "symptom_type": payload.symptom_type,
            "severity": payload.severity,
            "duration_notes": payload.duration_notes,
        },
    )
    return SymptomLogRead.from_event_and_detail(event, detail)


@router.get("", response_model=list[SymptomLogRead])
async def list_symptom_logs(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[SymptomLogRead]:
    events = await health_event_service.get_events(
        db,
        patient.id,
        event_type=EventType.symptom,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return [SymptomLogRead.from_event_and_detail(event, detail) for event, detail in events]


@router.get("/{event_id}", response_model=SymptomLogRead)
async def get_symptom_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> SymptomLogRead:
    event = await _get_owned_symptom_event_or_404(db, patient, event_id)
    detail = await health_event_service.get_event_detail(db, event)
    return SymptomLogRead.from_event_and_detail(event, detail)


@router.put("/{event_id}", response_model=SymptomLogRead)
async def update_symptom_log(
    event_id: uuid.UUID,
    payload: SymptomLogUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> SymptomLogRead:
    event = await _get_owned_symptom_event_or_404(db, patient, event_id)

    updates = payload.model_dump(exclude_unset=True)
    event_updates = {key: updates[key] for key in ("event_timestamp", "notes") if key in updates}
    detail_updates = {key: updates[key] for key in _DETAIL_FIELDS if key in updates}

    updated_event, updated_detail = await health_event_service.update_event(
        db, event, event_updates=event_updates, detail_updates=detail_updates
    )
    return SymptomLogRead.from_event_and_detail(updated_event, updated_detail)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symptom_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> None:
    event = await _get_owned_symptom_event_or_404(db, patient, event_id)
    await health_event_service.delete_event(db, event)
