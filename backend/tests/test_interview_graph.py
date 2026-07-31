import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from httpx import AsyncClient
from langgraph.checkpoint.memory import InMemorySaver
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.schemas.assessment import ClinicalAssessment
from app.clinical_reasoning.schemas.context import (
    AdherenceSummary,
    DemographicsSummary,
    DiabetesHistorySummary,
    LifestyleSummary,
    PatientContext,
    TimelineSummary,
)
from app.clinical_reasoning.schemas.data_quality import DataQuality, DataQualityReport
from app.clinical_reasoning.schemas.findings import MissingInformation
from app.interview.graph.build import build_interview_graph
from app.interview.graph.nodes import MAX_INTERVIEW_TURNS, check_sufficiency, load_context
from app.interview.graph.state import InterviewState
from tests.test_patients import auth_headers, register_patient
from tests.test_timeline import _create_glucose


def _today_at(hour: int) -> str:
    today = datetime.now(UTC).date()
    return datetime(today.year, today.month, today.day, hour, tzinfo=UTC).isoformat()


async def _register(client: AsyncClient, email: str) -> tuple[str, uuid.UUID]:
    reg = await register_patient(client, email)
    token = reg["tokens"]["access_token"]
    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    patient_id = uuid.UUID(profile.json()["patient"]["id"])
    return token, patient_id


@asynccontextmanager
async def _session_cm(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    yield session


def _blank_context(patient_id: uuid.UUID) -> PatientContext:
    return PatientContext(
        patient_id=patient_id,
        version=1,
        generated_at=datetime.now(UTC),
        demographics=DemographicsSummary(
            age=None,
            sex=None,
            height_cm=None,
            weight_kg=None,
            bmi=None,
            occupation=None,
            work_schedule=None,
        ),
        diabetes_history=DiabetesHistorySummary(
            diabetes_type=None,
            years_since_diagnosis=None,
            family_history=False,
            family_history_notes=None,
            latest_hba1c=None,
            latest_blood_pressure_systolic=None,
            latest_blood_pressure_diastolic=None,
            latest_cholesterol=None,
            has_kidney_disease=False,
            has_eye_disease=False,
            has_neuropathy=False,
            comorbidities=[],
        ),
        medications=[],
        latest_glucose=None,
        last_7_day_summary=TimelineSummary(
            total_events=0,
            glucose_reading_count=0,
            glucose_average_mg_dl=None,
            glucose_stdev_mg_dl=None,
            meals_logged_count=0,
            meals_logged_today=0,
            last_meal_at=None,
            exercise_total_minutes=0,
            exercise_session_count=0,
            sleep_average_hours=None,
            last_sleep_at=None,
            average_stress_level=None,
            symptoms_logged_count=0,
        ),
        adherence_summary=AdherenceSummary(
            doses_taken_7day=0, doses_missed_7day=0, adherence_pct_7day=None
        ),
        active_symptoms=[],
        lifestyle_summary=LifestyleSummary(
            sleep_hours_avg=None,
            exercise_frequency=None,
            exercise_type=None,
            smoking_status=None,
            alcohol_use=None,
            stress_level_baseline=None,
            meal_schedule_notes=None,
        ),
        goals=[],
        recent_patterns=[],
        known_barriers=[],
    )


def _assessment_with_gaps(missing_types: list[str]) -> dict:
    patient_id = uuid.uuid4()
    quality = DataQuality(
        completeness=1.0, freshness=1.0, consistency=1.0, reliability=1.0, coverage_label=None
    )
    assessment = ClinicalAssessment(
        version=1,
        context_version=1,
        generated_at=datetime.now(UTC),
        patient_context=_blank_context(patient_id),
        data_quality=DataQualityReport(by_type={}, overall=quality),
        contradictions=[],
        missing_information=[
            MissingInformation(event_type=event_type, reason="test gap", severity="medium")
            for event_type in missing_types
        ],
        uncertainties=[],
    )
    return assessment.model_dump(mode="json")


def _state(turns: int, assessment: dict | None, resolved: list[str]) -> InterviewState:
    return {
        "session_id": uuid.uuid4(),
        "patient_id": uuid.uuid4(),
        "intent": None,
        "assessment": assessment,
        "turns": [
            {"role": "agent", "content": "", "timestamp": datetime.now(UTC)} for _ in range(turns)
        ],
        "pending_questions": [],
        "resolved_this_session": resolved,
        "candidate_facts": [],
    }


# --- check_sufficiency: pure routing logic, no DB/LLM involved -------------


def test_check_sufficiency_continues_when_gaps_outstanding() -> None:
    state = _state(turns=1, assessment=_assessment_with_gaps(["glucose", "sleep"]), resolved=[])
    assert check_sufficiency(state) == "continue"


def test_check_sufficiency_sufficient_when_all_gaps_resolved() -> None:
    state = _state(
        turns=1,
        assessment=_assessment_with_gaps(["glucose", "sleep"]),
        resolved=["glucose", "sleep"],
    )
    assert check_sufficiency(state) == "sufficient"


def test_check_sufficiency_continues_when_assessment_not_loaded_yet() -> None:
    state = _state(turns=1, assessment=None, resolved=[])
    assert check_sufficiency(state) == "continue"


def test_check_sufficiency_sufficient_when_no_gaps_at_all() -> None:
    state = _state(turns=1, assessment=_assessment_with_gaps([]), resolved=[])
    assert check_sufficiency(state) == "sufficient"


def test_check_sufficiency_turn_limit_overrides_outstanding_gaps() -> None:
    state = _state(
        turns=MAX_INTERVIEW_TURNS, assessment=_assessment_with_gaps(["glucose"]), resolved=[]
    )
    assert check_sufficiency(state) == "sufficient"


def test_check_sufficiency_below_turn_limit_with_gaps_still_continues() -> None:
    state = _state(
        turns=MAX_INTERVIEW_TURNS - 1, assessment=_assessment_with_gaps(["glucose"]), resolved=[]
    )
    assert check_sufficiency(state) == "continue"


# --- load_context: populates `assessment` from the real Clinical Reasoning
# Service, using the test's own rolled-back DB session via config injection.


async def test_load_context_populates_assessment_from_clinical_reasoning_service(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "load-context@example.com")
    await _create_glucose(client, token, _today_at(8), value=120)

    state = _state(turns=0, assessment=None, resolved=[])
    state["patient_id"] = patient_id
    config = {"configurable": {"db_session_factory": lambda: _session_cm(db_session)}}

    update = await load_context(state, config)

    assessment = update["assessment"]
    assert assessment is not None
    assert assessment["version"] == 1
    assert assessment["patient_context"]["patient_id"] == str(patient_id)
    assert assessment["patient_context"]["latest_glucose"]["value"] == 120


# --- Full (partial) graph: proves the classify_intent -> load_context ->
# ask_question <-> receive_answer wiring compiles and actually terminates,
# via the turn-count safety limit, before Prompt 2 replaces the stub loop.


async def test_graph_compiles_and_terminates_via_turn_limit(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "graph-e2e@example.com")

    graph = build_interview_graph(InMemorySaver())
    session_id = uuid.uuid4()
    initial_state = _state(turns=0, assessment=None, resolved=[])
    initial_state["session_id"] = session_id
    initial_state["patient_id"] = patient_id
    config = {
        "configurable": {
            "thread_id": str(session_id),
            "db_session_factory": lambda: _session_cm(db_session),
        }
    }

    final_state = await graph.ainvoke(initial_state, config)

    # ask_question/receive_answer each append exactly one turn per pass and
    # only receive_answer's turn triggers the check_sufficiency routing, so
    # the loop always stops at the first even turn count >= the limit (16,
    # not 15, for MAX_INTERVIEW_TURNS=15) — not because it's unbounded, but
    # because the limit is only ever checked after a matched ask+answer pair.
    assert len(final_state["turns"]) == MAX_INTERVIEW_TURNS + 1
    assert final_state["assessment"] is not None
    assert final_state["intent"] is None
