from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class InterviewSessionStatus(str, Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"


class InterviewSession(Base, UUIDPKMixin, TimestampMixin):
    """One row per LangGraph interview run. `id` doubles as the LangGraph
    `thread_id` the Postgres checkpointer keys its own state on — this row
    is our queryable record of the session (who, when, how it ended); the
    turn-by-turn InterviewState lives in the checkpointer's own tables, not
    here.
    """

    __tablename__ = "interview_sessions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[InterviewSessionStatus] = mapped_column(
        SAEnum(InterviewSessionStatus, name="interview_session_status"),
        nullable=False,
        default=InterviewSessionStatus.active,
    )
    # Final interview outcome (summary, resolved items, etc.) — populated only
    # once the session ends; Prompt 2/3's summarize node is what will write it.
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    patient: Mapped[Patient] = relationship()
