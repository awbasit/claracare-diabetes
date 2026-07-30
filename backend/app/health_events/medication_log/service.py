import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.models.enums import EventType
from app.health_events.models.medication_log import MedicationLog
from app.health_events.services.health_event_service import register_detail_service


class MedicationLogService:
    async def create_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, detail_data: dict[str, Any]
    ) -> MedicationLog:
        log = MedicationLog(health_event_id=health_event_id, **detail_data)
        db.add(log)
        await db.flush()
        return log

    async def get_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID
    ) -> MedicationLog | None:
        result = await db.execute(
            select(MedicationLog).where(MedicationLog.health_event_id == health_event_id)
        )
        return result.scalar_one_or_none()

    async def update_detail(
        self, db: AsyncSession, health_event_id: uuid.UUID, updates: dict[str, Any]
    ) -> MedicationLog:
        log = await self.get_detail(db, health_event_id)
        if log is None:
            raise ValueError(f"No medication log attached to health event {health_event_id}")
        for field, value in updates.items():
            setattr(log, field, value)
        await db.flush()
        return log


medication_log_service = MedicationLogService()
register_detail_service(EventType.medication, medication_log_service)
