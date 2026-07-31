from datetime import UTC, datetime
from typing import Any, Literal

from langchain_core.runnables import RunnableConfig

from app.clinical_reasoning.schemas.assessment import ClinicalAssessment
from app.clinical_reasoning.services import clinical_reasoning_service
from app.database.session import AsyncSessionLocal
from app.interview.graph.state import InterviewState

# Design doc §9 turn-count safety limit — a hard stop so a stuck/looping
# interview can't run forever regardless of what check_sufficiency's gap
# analysis decides.
MAX_INTERVIEW_TURNS = 15


async def classify_intent(state: InterviewState) -> dict[str, Any]:
    """Stub — Prompt 2 replaces this body with the real LLM classification
    call. Kept async (rather than sync-then-wrapped) since the eventual LLM
    call is async, so Prompt 2 only has to fill in the model call itself,
    not change this node's signature or how it's wired into the graph.
    """
    return {"intent": None}


async def load_context(state: InterviewState, config: RunnableConfig) -> dict[str, Any]:
    """Populates `assessment` by generating a fresh Clinical Reasoning Service
    snapshot for this patient, every time an interview starts.

    Deliberately does NOT reuse `get_latest_snapshot` — the moment a patient
    starts an interview is exactly the moment the picture needs to be as
    current as possible, and a stale cached snapshot could disagree with
    what the live-query tool layer reports moments later in the same
    conversation. Snapshots are cheap, versioned, and immutable (see
    PatientContextSnapshot), so generating a new one per interview start has
    no real downside beyond one extra row.
    """
    session_factory = config.get("configurable", {}).get("db_session_factory", AsyncSessionLocal)
    async with session_factory() as db:
        assessment = await clinical_reasoning_service.generate_assessment(db, state["patient_id"])
    return {"assessment": assessment.model_dump(mode="json")}


async def ask_question(state: InterviewState) -> dict[str, Any]:
    """Pass-through stub — Prompt 2 replaces this with real LLM-driven
    question generation. Appends a placeholder turn purely so the compiled
    graph's ask_question/receive_answer loop has something for
    check_sufficiency's turn-count safety limit to count, proving the loop
    and its exit route work end to end before Prompt 2 lands.
    """
    turn = {"role": "agent", "content": "", "timestamp": datetime.now(UTC)}
    return {"turns": [turn]}


async def receive_answer(state: InterviewState) -> dict[str, Any]:
    """Pass-through stub — Prompt 2 replaces this with real patient-input
    handling (likely via an `interrupt()`). See ask_question for why it still
    appends a placeholder turn.
    """
    turn = {"role": "patient", "content": "", "timestamp": datetime.now(UTC)}
    return {"turns": [turn]}


async def summarize(state: InterviewState) -> dict[str, Any]:
    """Pass-through stub — a later milestone fills in real end-of-interview
    summarization. The graph needs a terminal node to route to once
    check_sufficiency says enough has been resolved (or the turn limit hits),
    so this exists purely to give it one.
    """
    return {}


def check_sufficiency(state: InterviewState) -> Literal["continue", "sufficient"]:
    """Pure Python routing function (no LLM) used as a conditional edge after
    receive_answer: decides whether to loop back to ask_question or proceed
    to summarize.

    Two, independently-sufficient stop conditions:
      - the turn-count safety limit has been hit, or
      - every gap/contradiction the loaded assessment flagged has since been
        marked resolved (by whatever writes to `resolved_this_session` —
        Prompt 2's territory).
    """
    if len(state["turns"]) >= MAX_INTERVIEW_TURNS:
        return "sufficient"

    assessment_data = state.get("assessment")
    if assessment_data is None:
        return "continue"

    assessment = ClinicalAssessment.model_validate(assessment_data)
    resolved = set(state.get("resolved_this_session", []))

    outstanding_gaps = [
        gap for gap in assessment.missing_information if gap.event_type not in resolved
    ]
    outstanding_contradictions = [
        contradiction
        for contradiction in assessment.contradictions
        if str(contradiction.id) not in resolved
    ]
    if outstanding_gaps or outstanding_contradictions:
        return "continue"
    return "sufficient"
