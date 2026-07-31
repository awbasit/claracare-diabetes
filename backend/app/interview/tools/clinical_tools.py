import uuid
from typing import Any

from langchain_core.tools import BaseTool, tool

from app.clinical_reasoning.services import clinical_reasoning_service
from app.interview.db import SessionFactory


def build_patient_tools(patient_id: uuid.UUID, session_factory: SessionFactory) -> list[BaseTool]:
    """Builds the read-only Clinical Tool Layer (Milestone 3.2) for one
    patient's interview session.

    `patient_id` and `session_factory` are bound via closure rather than
    exposed as tool parameters: an LLM-callable tool's schema must never let
    the model choose *which* patient's data a query touches — only the
    genuinely safe per-call knobs (like `days`) are part of what the model
    sees and can set.

    Each tool wraps the corresponding Clinical Reasoning Service live-query
    method (never the DB directly) and opens its own short-lived session per
    call, since these tools may be invoked many times across a single
    checkpointed interview that can span an arbitrarily long wall-clock gap
    between turns.
    """

    @tool
    async def get_today_glucose() -> dict[str, Any]:
        """Get the patient's glucose readings logged so far today, live from
        the database — not the cached clinical context snapshot."""
        async with session_factory() as db:
            summary = await clinical_reasoning_service.get_today_glucose(db, patient_id)
        return summary.model_dump(mode="json")

    @tool
    async def get_recent_meals(days: int = 3) -> dict[str, Any]:
        """Get the patient's meals logged over the trailing `days` days (default 3)."""
        async with session_factory() as db:
            summary = await clinical_reasoning_service.get_recent_meals(db, patient_id, days=days)
        return summary.model_dump(mode="json")

    @tool
    async def get_medication_adherence(days: int = 7) -> dict[str, Any]:
        """Get the patient's medication dose adherence over the trailing
        `days` days (default 7): doses taken vs. missed and the adherence
        percentage."""
        async with session_factory() as db:
            summary = await clinical_reasoning_service.get_medication_adherence(
                db, patient_id, days=days
            )
        return summary.model_dump(mode="json")

    @tool
    async def get_sleep_summary(days: int = 7) -> dict[str, Any]:
        """Get a summary of the patient's sleep logged over the trailing
        `days` days (default 7): average hours, last night's hours, and
        average sleep quality."""
        async with session_factory() as db:
            summary = await clinical_reasoning_service.get_sleep_summary(db, patient_id, days=days)
        return summary.model_dump(mode="json")

    @tool
    async def get_latest_vitals() -> dict[str, Any] | None:
        """Get the patient's most recently logged vitals (weight, blood
        pressure, heart rate), or null if none have ever been logged."""
        async with session_factory() as db:
            summary = await clinical_reasoning_service.get_latest_vitals(db, patient_id)
        return summary.model_dump(mode="json") if summary is not None else None

    @tool
    async def get_recent_symptoms(days: int = 7) -> dict[str, Any]:
        """Get the patient's symptoms logged over the trailing `days` days (default 7)."""
        async with session_factory() as db:
            summary = await clinical_reasoning_service.get_recent_symptoms(
                db, patient_id, days=days
            )
        return summary.model_dump(mode="json")

    return [
        get_today_glucose,
        get_recent_meals,
        get_medication_adherence,
        get_sleep_summary,
        get_latest_vitals,
        get_recent_symptoms,
    ]
