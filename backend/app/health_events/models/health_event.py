from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import EventSource, EventType
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.glucose_log import GlucoseLog


class HealthEvent(UUIDPKMixin, TimestampMixin, Base):
    """The central timeline row. Each event type attaches exactly one detail row
    (e.g. GlucoseLog) keyed off health_event_id — see health_event_service's
    dispatch registry for how a detail row is created/read/updated per type.
    """

    __tablename__ = "health_events"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="health_event_type"), nullable=False, index=True
    )
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[EventSource] = mapped_column(
        Enum(EventSource, name="health_event_source"), nullable=False, default=EventSource.manual
    )

    glucose_log: Mapped[GlucoseLog | None] = relationship(
        back_populates="health_event",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
