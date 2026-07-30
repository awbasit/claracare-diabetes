from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.health_events.models.enums import SymptomSeverity, SymptomType
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.health_events.models.health_event import HealthEvent


class SymptomLog(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "symptom_logs"

    health_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("health_events.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    symptom_type: Mapped[SymptomType] = mapped_column(
        Enum(SymptomType, name="symptom_type"), nullable=False
    )
    severity: Mapped[SymptomSeverity] = mapped_column(
        Enum(SymptomSeverity, name="symptom_severity"), nullable=False
    )
    duration_notes: Mapped[str | None] = mapped_column(Text)

    health_event: Mapped[HealthEvent] = relationship(back_populates="symptom_log")
