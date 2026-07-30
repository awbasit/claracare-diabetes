import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.exercise.schemas import ExerciseLogCreate, ExerciseLogRead, ExerciseLogUpdate
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent
from app.health_events.services import health_event_service
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/exercise", tags=["exercise"])

_DETAIL_FIELDS = (
    "exercise_type",
    "duration_minutes",
    "intensity",
    "calories_burned",
    "heart_rate_avg",
)


async def _get_owned_exercise_event_or_404(
    db: AsyncSession, patient: Patient, event_id: uuid.UUID
) -> HealthEvent:
    event = await health_event_service.get_own_event_of_type(
        db, patient.id, event_id, EventType.exercise
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise log not found")
    return event


@router.post("", response_model=ExerciseLogRead, status_code=status.HTTP_201_CREATED)
async def create_exercise_log(
    payload: ExerciseLogCreate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> ExerciseLogRead:
    event, detail = await health_event_service.create_event(
        db,
        patient_id=patient.id,
        event_type=EventType.exercise,
        event_timestamp=payload.event_timestamp,
        notes=payload.notes,
        detail_data={
            "exercise_type": payload.exercise_type,
            "duration_minutes": payload.duration_minutes,
            "intensity": payload.intensity,
            "calories_burned": payload.calories_burned,
            "heart_rate_avg": payload.heart_rate_avg,
        },
    )
    return ExerciseLogRead.from_event_and_detail(event, detail)


@router.get("", response_model=list[ExerciseLogRead])
async def list_exercise_logs(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[ExerciseLogRead]:
    events = await health_event_service.get_events(
        db,
        patient.id,
        event_types=[EventType.exercise],
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return [ExerciseLogRead.from_event_and_detail(event, detail) for event, detail in events]


@router.get("/{event_id}", response_model=ExerciseLogRead)
async def get_exercise_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> ExerciseLogRead:
    event = await _get_owned_exercise_event_or_404(db, patient, event_id)
    detail = await health_event_service.get_event_detail(db, event)
    return ExerciseLogRead.from_event_and_detail(event, detail)


@router.put("/{event_id}", response_model=ExerciseLogRead)
async def update_exercise_log(
    event_id: uuid.UUID,
    payload: ExerciseLogUpdate,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> ExerciseLogRead:
    event = await _get_owned_exercise_event_or_404(db, patient, event_id)

    updates = payload.model_dump(exclude_unset=True)
    event_updates = {key: updates[key] for key in ("event_timestamp", "notes") if key in updates}
    detail_updates = {key: updates[key] for key in _DETAIL_FIELDS if key in updates}

    updated_event, updated_detail = await health_event_service.update_event(
        db, event, event_updates=event_updates, detail_updates=detail_updates
    )
    return ExerciseLogRead.from_event_and_detail(updated_event, updated_detail)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_log(
    event_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> None:
    event = await _get_owned_exercise_event_or_404(db, patient, event_id)
    await health_event_service.delete_event(db, event)
