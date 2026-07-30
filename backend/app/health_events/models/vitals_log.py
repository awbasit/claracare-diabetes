from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class VitalsLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "vitals_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    weight_kg: Mapped[float | None] = mapped_column(Float)
    blood_pressure_systolic: Mapped[int | None] = mapped_column(SmallInteger)
    blood_pressure_diastolic: Mapped[int | None] = mapped_column(SmallInteger)
    heart_rate: Mapped[int | None] = mapped_column(SmallInteger)

    health_event: Mapped[HealthEvent] = relationship(back_populates="vitals_log")
