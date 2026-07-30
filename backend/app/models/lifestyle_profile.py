from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class LifestyleProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "lifestyle_profiles"
    __table_args__ = (
        CheckConstraint(
            "stress_level_baseline BETWEEN 1 AND 10",
            name="ck_lifestyle_profiles_stress_level_range",
        ),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    sleep_hours_avg: Mapped[float | None] = mapped_column(Float)
    exercise_frequency: Mapped[str | None] = mapped_column(String(100))
    exercise_type: Mapped[str | None] = mapped_column(String(100))
    smoking_status: Mapped[str | None] = mapped_column(String(50))
    alcohol_use: Mapped[str | None] = mapped_column(String(50))
    stress_level_baseline: Mapped[int | None] = mapped_column(SmallInteger)
    meal_schedule_notes: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[Patient] = relationship(back_populates="lifestyle_profile")
