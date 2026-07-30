from datetime import UTC, datetime, timedelta
from datetime import date as date_type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_patient
from app.database.session import get_db
from app.health_events.models.enums import EventType
from app.health_events.services import health_event_service
from app.health_events.timeline import service as timeline_service
from app.health_events.timeline.schemas import DailySummary, TimelineEventRead
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/me/timeline", tags=["timeline"])


@router.get("", response_model=list[TimelineEventRead])
async def get_timeline(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    event_types: list[EventType] | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> list[TimelineEventRead]:
    if start is None or end is None:
        today = datetime.now(UTC).date()
        today_start = datetime(today.year, today.month, today.day, tzinfo=UTC)
        if start is None:
            start = today_start
        if end is None:
            end = today_start + timedelta(days=1)

    events = await health_event_service.get_events(
        db,
        patient.id,
        event_types=event_types,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    return [TimelineEventRead.from_event_and_detail(event, detail) for event, detail in events]


@router.get("/summary", response_model=DailySummary)
async def get_timeline_summary(
    date: date_type | None = Query(None),
    patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
) -> DailySummary:
    target_date = date if date is not None else datetime.now(UTC).date()
    return await timeline_service.get_daily_summary(db, patient.id, target_date)
