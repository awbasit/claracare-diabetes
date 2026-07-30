from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import SleepQuality
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class SleepLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "sleep_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    bedtime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wake_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hours_slept: Mapped[float] = mapped_column(Float, nullable=False)
    quality: Mapped[SleepQuality] = mapped_column(
        Enum(SleepQuality, name="sleep_quality"), nullable=False
    )
    night_awakenings: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

    health_event: Mapped[HealthEvent] = relationship(back_populates="sleep_log")
