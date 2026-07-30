from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.enums import Sex

if TYPE_CHECKING:
    from app.models.baseline_assessment import BaselineAssessment
    from app.models.lifestyle_profile import LifestyleProfile
    from app.models.medical_history import MedicalHistory
    from app.models.medication import Medication
    from app.models.user import User


class Patient(UUIDPKMixin, TimestampMixin, Base):
    """patients.id is the stable anchor future HealthEvent rows will key off (patient_id FK)."""

    __tablename__ = "patients"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    age: Mapped[int | None] = mapped_column(SmallInteger)
    sex: Mapped[Sex | None] = mapped_column(Enum(Sex, name="sex"))
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    bmi: Mapped[float | None] = mapped_column(Float)
    occupation: Mapped[str | None] = mapped_column(String(255))
    work_schedule: Mapped[str | None] = mapped_column(String(255))

    user: Mapped[User] = relationship(back_populates="patient")
    medical_history: Mapped[MedicalHistory | None] = relationship(
        back_populates="patient", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )
    medications: Mapped[list[Medication]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", passive_deletes=True
    )
    lifestyle_profile: Mapped[LifestyleProfile | None] = relationship(
        back_populates="patient", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )
    baseline_assessment: Mapped[BaselineAssessment | None] = relationship(
        back_populates="patient", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )
