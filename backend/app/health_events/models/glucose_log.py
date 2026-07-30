from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import GlucoseReadingType, GlucoseUnit
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class GlucoseLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "glucose_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[GlucoseUnit] = mapped_column(
        Enum(GlucoseUnit, name="glucose_unit"), nullable=False
    )
    reading_type: Mapped[GlucoseReadingType] = mapped_column(
        Enum(GlucoseReadingType, name="glucose_reading_type"), nullable=False
    )
    confidence: Mapped[float | None] = mapped_column(Float)
    manually_entered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    health_event: Mapped[HealthEvent] = relationship(back_populates="glucose_log")
