import operator
import uuid
from datetime import datetime
from typing import Annotated, Any, Literal, TypedDict

# One of routine_checkin/symptom_report/question/medication_concern, per
# design doc §9 — kept as a plain Literal (not an Enum) because LangGraph's
# checkpoint serializer warns that arbitrary custom classes (Enums included)
# are "unregistered types" it may stop deserializing in a future version;
# every field on this state is deliberately restricted to plain
# str/int/float/bool/None/list/dict plus the handful of natively-supported
# extension types (datetime, uuid) for exactly that reason.
Intent = Literal["routine_checkin", "symptom_report", "question", "medication_concern"]


class Turn(TypedDict):
    role: Literal["patient", "agent"]
    content: str
    timestamp: datetime


class CandidateFact(TypedDict):
    """A working-memory fact noted via `save_memory` during this session —
    not yet promoted to durable episodic memory (Milestone 3.3). The shape
    here is provisional: only `save_memory`'s own milestone owns deciding
    what richer structure (category, confidence, etc.) this needs; this
    milestone only needs somewhere for it to land.
    """

    fact: str
    noted_at: datetime
    source_turn: int


class InterviewState(TypedDict):
    session_id: uuid.UUID
    patient_id: uuid.UUID
    intent: Intent | None

    # The Milestone 3.1 ClinicalAssessment, stored as its `model_dump(mode=
    # "json")` dict rather than the live pydantic object — same reasoning as
    # `Intent` above: keep every persisted field a plain, natively-serializable
    # type. Reconstruct with `ClinicalAssessment.model_validate(...)` at the
    # point of use.
    assessment: dict[str, Any] | None

    turns: Annotated[list[Turn], operator.add]
    pending_questions: list[str]
    # Identifiers of resolved gaps/contradictions this session — each entry is
    # either a MissingInformation.event_type or a str(Contradiction.id).
    resolved_this_session: Annotated[list[str], operator.add]
    candidate_facts: Annotated[list[CandidateFact], operator.add]
