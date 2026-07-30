from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import MealType
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class MealLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "meal_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType, name="meal_type"), nullable=False)
    food_items: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_carbs_g: Mapped[float | None] = mapped_column(Float)
    estimated_calories: Mapped[int | None] = mapped_column(Integer)
    portion_size: Mapped[str | None] = mapped_column(String(255))
    drink: Mapped[str | None] = mapped_column(String(255))

    health_event: Mapped[HealthEvent] = relationship(back_populates="meal_log")
