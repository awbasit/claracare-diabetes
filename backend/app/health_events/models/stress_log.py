from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import Mood
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class StressLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "stress_logs"
    __table_args__ = (
        CheckConstraint("stress_level BETWEEN 1 AND 10", name="ck_stress_logs_stress_level_range"),
        CheckConstraint(
            "energy_level IS NULL OR energy_level BETWEEN 1 AND 10",
            name="ck_stress_logs_energy_level_range",
        ),
    )

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    stress_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    mood: Mapped[Mood] = mapped_column(Enum(Mood, name="mood"), nullable=False)
    energy_level: Mapped[int | None] = mapped_column(SmallInteger)

    health_event: Mapped[HealthEvent] = relationship(back_populates="stress_log")
