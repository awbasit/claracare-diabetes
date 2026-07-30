import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.medication_log.schemas import (
    MedicationLogCreate,
    MedicationLogRead,
    MedicationLogUpdate,
)
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent
from app.health_events.services import health_event_service
from app.models.patient import Patient
from app.patients import service as patients_service

router = APIRouter(prefix="/api/patients/me/medication-log", tags=["medication-log"])

_DETAIL_FIELDS = ("medication_id", "scheduled_time", "actual_time", "taken", "missed_reason")


async def _get_owned_medication_log_event_or_404(
    db: AsyncSession, patient: Patient, event_id: uuid.UUID
) -> HealthEvent:
    event = await health_event_service.get_own_event_of_type(
        db, patient.id, event_id, EventType.medication
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medication log not found"
        )
    return event


async def _ensure_owned_medication(
    db: AsyncSession, patient: Patient, medication_id: uuid.UUID
) -> None:
    # medication_id references Sprint 1's master medication list — a client
    # could otherwise reference another patient's medication by id.
    medication = await patients_service.get_own_medication(db, patient.id, medication_id)
    if medication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")


@router.post("", response_model=MedicationLogRead, status_code=status.HTTP_201_CREATED)
async def create_medication_log(
    payload: MedicationLogCreate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> MedicationLogRead:
    await _ensure_owned_medication(db, patient, payload.medication_id)

    event, detail = await health_event_service.create_event(
        db,
        patient_id=patient.id,
        event_type=EventType.medication,
        event_timestamp=payload.event_timestamp,
        notes=payload.notes,
        detail_data={
            "medication_id": payload.medication_id,
            "scheduled_time": payload.scheduled_time,
            "actual_time": payload.actual_time,
            "taken": payload.taken,
            "missed_reason": payload.missed_reason,
        },
    )
    return MedicationLogRead.from_event_and_detail(event, detail)


@router.get("", response_model=list[MedicationLogRead])
async def list_medication_logs(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[MedicationLogRead]:
    events = await health_event_service.get_events(
        db,
        patient.id,
        event_type=EventType.medication,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return [MedicationLogRead.from_event_and_detail(event, detail) for event, detail in events]


@router.get("/{event_id}", response_model=MedicationLogRead)
async def get_medication_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> MedicationLogRead:
    event = await _get_owned_medication_log_event_or_404(db, patient, event_id)
    detail = await health_event_service.get_event_detail(db, event)
    return MedicationLogRead.from_event_and_detail(event, detail)


@router.put("/{event_id}", response_model=MedicationLogRead)
async def update_medication_log(
    event_id: uuid.UUID,
    payload: MedicationLogUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> MedicationLogRead:
    event = await _get_owned_medication_log_event_or_404(db, patient, event_id)

    updates = payload.model_dump(exclude_unset=True)
    if "medication_id" in updates:
        await _ensure_owned_medication(db, patient, updates["medication_id"])

    event_updates = {key: updates[key] for key in ("event_timestamp", "notes") if key in updates}
    detail_updates = {key: updates[key] for key in _DETAIL_FIELDS if key in updates}

    updated_event, updated_detail = await health_event_service.update_event(
        db, event, event_updates=event_updates, detail_updates=detail_updates
    )
    return MedicationLogRead.from_event_and_detail(updated_event, updated_detail)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> None:
    event = await _get_owned_medication_log_event_or_404(db, patient, event_id)
    await health_event_service.delete_event(db, event)
