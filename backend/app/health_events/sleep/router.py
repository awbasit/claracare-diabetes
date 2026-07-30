import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent
from app.health_events.services import health_event_service
from app.health_events.sleep.schemas import SleepLogCreate, SleepLogRead, SleepLogUpdate
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/sleep", tags=["sleep"])

_DETAIL_FIELDS = ("bedtime", "wake_time", "hours_slept", "quality", "night_awakenings")


async def _get_owned_sleep_event_or_404(
    db: AsyncSession, patient: Patient, event_id: uuid.UUID
) -> HealthEvent:
    event = await health_event_service.get_own_event_of_type(
        db, patient.id, event_id, EventType.sleep
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep log not found")
    return event


@router.post("", response_model=SleepLogRead, status_code=status.HTTP_201_CREATED)
async def create_sleep_log(
    payload: SleepLogCreate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> SleepLogRead:
    event, detail = await health_event_service.create_event(
        db,
        patient_id=patient.id,
        event_type=EventType.sleep,
        event_timestamp=payload.event_timestamp,
        notes=payload.notes,
        detail_data={
            "bedtime": payload.bedtime,
            "wake_time": payload.wake_time,
            "hours_slept": payload.hours_slept,
            "quality": payload.quality,
            "night_awakenings": payload.night_awakenings,
        },
    )
    return SleepLogRead.from_event_and_detail(event, detail)


@router.get("", response_model=list[SleepLogRead])
async def list_sleep_logs(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[SleepLogRead]:
    events = await health_event_service.get_events(
        db,
        patient.id,
        event_types=[EventType.sleep],
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return [SleepLogRead.from_event_and_detail(event, detail) for event, detail in events]


@router.get("/{event_id}", response_model=SleepLogRead)
async def get_sleep_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> SleepLogRead:
    event = await _get_owned_sleep_event_or_404(db, patient, event_id)
    detail = await health_event_service.get_event_detail(db, event)
    return SleepLogRead.from_event_and_detail(event, detail)


@router.put("/{event_id}", response_model=SleepLogRead)
async def update_sleep_log(
    event_id: uuid.UUID,
    payload: SleepLogUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> SleepLogRead:
    event = await _get_owned_sleep_event_or_404(db, patient, event_id)

    updates = payload.model_dump(exclude_unset=True)
    event_updates = {key: updates[key] for key in ("event_timestamp", "notes") if key in updates}
    detail_updates = {key: updates[key] for key in _DETAIL_FIELDS if key in updates}

    updated_event, updated_detail = await health_event_service.update_event(
        db, event, event_updates=event_updates, detail_updates=detail_updates
    )
    return SleepLogRead.from_event_and_detail(updated_event, updated_detail)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sleep_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> None:
    event = await _get_owned_sleep_event_or_404(db, patient, event_id)
    await health_event_service.delete_event(db, event)
