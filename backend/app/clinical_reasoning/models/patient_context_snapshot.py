from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import UUIDPKMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class PatientContextSnapshot(Base, UUIDPKMixin):
    """One immutable row per (patient, version). `context` and `assessment`
    are both stored as full JSONB blobs (assessment already nests context —
    the duplication is deliberate, per the schema this table was specified
    against, so a caller needing just the context doesn't have to unpack the
    larger assessment blob). Rows are never updated after insert — a new
    context/assessment always gets the next version number, never an
    in-place edit — that immutability is what lets any past decision be
    traced back to the exact context it was made from.
    """

    __tablename__ = "patient_context_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "patient_id", "version", name="uq_patient_context_snapshots_patient_version"
        ),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    assessment: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    patient: Mapped[Patient] = relationship()
