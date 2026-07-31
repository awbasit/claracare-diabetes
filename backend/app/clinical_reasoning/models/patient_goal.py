from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.clinical_reasoning.models.enums import PatientGoalSource, PatientGoalStatus
from app.database.base import Base
from app.models.base import UUIDPKMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class PatientGoal(Base, UUIDPKMixin):
    """Holds only current goals, for fast lookup by the Context Service when
    assembling PatientContext.goals. The historical record of when/why a
    goal was set or changed belongs in the Clinical Reasoning Ledger (§4,
    §8 record_patient_goal()) — Milestone 3.4 scope, not built here.
    """

    __tablename__ = "patient_goals"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str | None] = mapped_column(Text)
    status: Mapped[PatientGoalStatus] = mapped_column(
        Enum(PatientGoalStatus, name="patient_goal_status"),
        nullable=False,
        default=PatientGoalStatus.active,
    )
    source: Mapped[PatientGoalSource] = mapped_column(
        Enum(PatientGoalSource, name="patient_goal_source"), nullable=False
    )
    set_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient: Mapped[Patient] = relationship()
