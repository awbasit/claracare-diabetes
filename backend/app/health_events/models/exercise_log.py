from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import ExerciseIntensity
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class ExerciseLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "exercise_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    exercise_type: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    intensity: Mapped[ExerciseIntensity] = mapped_column(
        Enum(ExerciseIntensity, name="exercise_intensity"), nullable=False
    )
    calories_burned: Mapped[int | None] = mapped_column(Integer)
    heart_rate_avg: Mapped[int | None] = mapped_column(SmallInteger)

    health_event: Mapped[HealthEvent] = relationship(back_populates="exercise_log")
