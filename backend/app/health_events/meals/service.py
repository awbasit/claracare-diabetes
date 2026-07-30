import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.models.enums import EventType
from app.health_events.models.meal_log import MealLog
from app.health_events.services.health_event_service import register_detail_service


class MealLogService:
    async def create_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, detail_data: dict[str, Any]
    ) -> MealLog:
        log = MealLog(health_event_id=health_event_id, **detail_data)
        db.add(log)
        await db.flush()
        return log

    async def get_details_for_events(
        self, db: AsyncSession, health_event_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, MealLog]:
        if not health_event_ids:
            return {}
        result = await db.execute(
            select(MealLog).where(MealLog.health_event_id.in_(health_event_ids))
        )
        return {log.health_event_id: log for log in result.scalars().all()}

    async def get_detail(self, db: AsyncSession, health_event_id: uuid.UUID) -> MealLog | None:
        details = await self.get_details_for_events(db, [health_event_id])
        return details.get(health_event_id)

    async def update_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, updates: dict[str, Any]
    ) -> MealLog:
        log = await self.get_detail(db, health_event_id)
        if log is None:
            raise ValueError(f"No meal log attached to health event {health_event_id}")
        for field, value in updates.items():
            setattr(log, field, value)
        await db.flush()
        return log


meal_log_service = MealLogService()
register_detail_service(EventType.meal, meal_log_service)
