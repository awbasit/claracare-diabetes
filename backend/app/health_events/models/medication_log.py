from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent
    from app.models.medication import Medication


class MedicationLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "medication_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    taken: Mapped[bool] = mapped_column(Boolean, nullable=False)
    missed_reason: Mapped[str | None] = mapped_column(Text)

    health_event: Mapped[HealthEvent] = relationship(back_populates="medication_log")
    # One-directional — no back_populates on Medication. Added for the
    # Clinical Reasoning Evidence Builder (§3.1), which needs the medication
    # name to render e.g. "Missed Metformin, Wednesday" and would otherwise
    # only have the bare medication_id FK to work with.
    medication: Mapped[Medication] = relationship()
