from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, SmallInteger, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.enums import DiabetesType

if TYPE_CHECKING:
    from app.models.patient import Patient


class MedicalHistory(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "medical_histories"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    diabetes_type: Mapped[DiabetesType | None] = mapped_column(
        Enum(DiabetesType, name="diabetes_type")
    )
    years_since_diagnosis: Mapped[int | None] = mapped_column(SmallInteger)
    family_history: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    family_history_notes: Mapped[str | None] = mapped_column(Text)
    latest_hba1c: Mapped[float | None] = mapped_column(Float)
    latest_blood_pressure_systolic: Mapped[int | None] = mapped_column(SmallInteger)
    latest_blood_pressure_diastolic: Mapped[int | None] = mapped_column(SmallInteger)
    latest_cholesterol: Mapped[float | None] = mapped_column(Float)
    has_kidney_disease: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_eye_disease: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_neuropathy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comorbidities: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    patient: Mapped[Patient] = relationship(back_populates="medical_history")
