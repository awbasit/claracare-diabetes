import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.models.enums import EventType
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.services.health_event_service import register_detail_service

# mg/dL <-> mmol/L conversion factor (mg/dL = mmol/L * molar mass of glucose / 10).
MG_DL_PER_MMOL_L = 18.0182


def mg_dl_to_mmol_l(value: float) -> float:
    return round(value / MG_DL_PER_MMOL_L, 2)


def mmol_l_to_mg_dl(value: float) -> float:
    return round(value * MG_DL_PER_MMOL_L, 1)


class GlucoseService:
    """Owns the glucose_logs detail table. Only health_event_service should
    call this — it's registered as that service's dispatch target for
    EventType.glucose, not meant to be used directly by routers.
    """

    async def create_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, detail_data: dict[str, Any]
    ) -> GlucoseLog:
        log = GlucoseLog(health_event_id=health_event_id, **detail_data)
        db.add(log)
        await db.flush()
        return log

    async def get_details_for_events(
        self, db: AsyncSession, health_event_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, GlucoseLog]:
        if not health_event_ids:
            return {}
        result = await db.execute(
            select(GlucoseLog).where(GlucoseLog.health_event_id.in_(health_event_ids))
        )
        return {log.health_event_id: log for log in result.scalars().all()}

    async def get_detail(self, db: AsyncSession, health_event_id: uuid.UUID) -> GlucoseLog | None:
        details = await self.get_details_for_events(db, [health_event_id])
        return details.get(health_event_id)

    async def update_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, updates: dict[str, Any]
    ) -> GlucoseLog:
        log = await self.get_detail(db, health_event_id)
        if log is None:
            raise ValueError(f"No glucose log attached to health event {health_event_id}")
        for field, value in updates.items():
            setattr(log, field, value)
        await db.flush()
        return log


glucose_service = GlucoseService()
register_detail_service(EventType.glucose, glucose_service)
