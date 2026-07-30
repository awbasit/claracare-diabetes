import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.models.enums import EventType
from app.health_events.models.exercise_log import ExerciseLog
from app.health_events.services.health_event_service import register_detail_service


class ExerciseLogService:
    async def create_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, detail_data: dict[str, Any]
    ) -> ExerciseLog:
        log = ExerciseLog(health_event_id=health_event_id, **detail_data)
        db.add(log)
        await db.flush()
        return log

    async def get_details_for_events(
        self, db: AsyncSession, health_event_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, ExerciseLog]:
        if not health_event_ids:
            return {}
        result = await db.execute(
            select(ExerciseLog).where(ExerciseLog.health_event_id.in_(health_event_ids))
        )
        return {log.health_event_id: log for log in result.scalars().all()}

    async def get_detail(self, db: AsyncSession, health_event_id: uuid.UUID) -> ExerciseLog | None:
        details = await self.get_details_for_events(db, [health_event_id])
        return details.get(health_event_id)

    async def update_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, updates: dict[str, Any]
    ) -> ExerciseLog:
        log = await self.get_detail(db, health_event_id)
        if log is None:
            raise ValueError(f"No exercise log attached to health event {health_event_id}")
        for field, value in updates.items():
            setattr(log, field, value)
        await db.flush()
        return log


exercise_log_service = ExerciseLogService()
register_detail_service(EventType.exercise, exercise_log_service)
