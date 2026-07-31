import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.services import clinical_reasoning_service
from app.interview.tools.clinical_tools import build_patient_tools
from tests.test_medication_log import _create_medication
from tests.test_patients import auth_headers, register_patient
from tests.test_timeline import (
    _create_glucose,
    _create_meal,
    _create_medication_log,
    _create_sleep,
    _create_symptom,
    _create_vitals,
)


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


# --- Each live-query tool proves it's a live query, not a snapshot read: a
# snapshot is generated first (capturing "nothing logged yet"), then an event
# is logged *after* that snapshot, then the tool is called and must reflect
# the new event even though the already-captured snapshot object obviously
# still shows the pre-event state. ------------------------------------------


async def test_get_today_glucose_reflects_event_logged_after_snapshot(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-glucose@example.com")
    stale_snapshot = await clinical_reasoning_service.generate_assessment(db_session, patient_id)
    assert stale_snapshot.patient_context.latest_glucose is None

    await _create_glucose(client, token, _today_at(9), value=145)

    result = await clinical_reasoning_service.get_today_glucose(db_session, patient_id)
    assert result.count == 1
    assert result.readings[0].value == 145
    assert result.average_mg_dl == 145
    assert stale_snapshot.patient_context.latest_glucose is None


async def test_get_recent_meals_reflects_event_logged_after_snapshot(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-meals@example.com")
    await clinical_reasoning_service.generate_assessment(db_session, patient_id)

    result_before = await clinical_reasoning_service.get_recent_meals(db_session, patient_id)
    assert result_before.count == 0

    await _create_meal(client, token, _today_at(8))

    result_after = await clinical_reasoning_service.get_recent_meals(db_session, patient_id)
    assert result_after.count == 1
    assert result_after.meals[0].food_items == "oatmeal"


async def test_get_medication_adherence_reflects_dose_logged_after_snapshot(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-medadherence@example.com")
    medication_id = await _create_medication(client, token)
    await clinical_reasoning_service.generate_assessment(db_session, patient_id)

    result_before = await clinical_reasoning_service.get_medication_adherence(
        db_session, patient_id
    )
    assert result_before.doses_taken == 0
    assert result_before.adherence_pct is None

    await _create_medication_log(client, token, medication_id, _today_at(9), taken=True)

    result_after = await clinical_reasoning_service.get_medication_adherence(db_session, patient_id)
    assert result_after.doses_taken == 1
    assert result_after.adherence_pct == 100.0


async def test_get_sleep_summary_reflects_event_logged_after_snapshot(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-sleep@example.com")
    await clinical_reasoning_service.generate_assessment(db_session, patient_id)

    result_before = await clinical_reasoning_service.get_sleep_summary(db_session, patient_id)
    assert result_before.nights_logged == 0
    assert result_before.last_night_hours is None

    await _create_sleep(client, token, _today_at(6))

    result_after = await clinical_reasoning_service.get_sleep_summary(db_session, patient_id)
    assert result_after.nights_logged == 1
    assert result_after.last_night_hours == 7.0
    assert result_after.average_quality_score == 3.0  # "good"


async def test_get_latest_vitals_reflects_event_logged_after_snapshot(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-vitals@example.com")
    await clinical_reasoning_service.generate_assessment(db_session, patient_id)

    assert await clinical_reasoning_service.get_latest_vitals(db_session, patient_id) is None

    await _create_vitals(client, token, _today_at(11))

    result_after = await clinical_reasoning_service.get_latest_vitals(db_session, patient_id)
    assert result_after is not None
    assert result_after.heart_rate == 70


async def test_get_recent_symptoms_reflects_event_logged_after_snapshot(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-symptoms@example.com")
    stale_snapshot = await clinical_reasoning_service.generate_assessment(db_session, patient_id)
    assert stale_snapshot.patient_context.active_symptoms == []

    await _create_symptom(client, token, _today_at(11))

    result = await clinical_reasoning_service.get_recent_symptoms(db_session, patient_id)
    assert result.count == 1
    assert result.symptoms[0].symptom_type.value == "fatigue"
    assert stale_snapshot.patient_context.active_symptoms == []


# --- Tool-layer wiring: the LangChain @tool objects delegate to the same
# service-layer functions above, with patient_id bound via closure (never a
# model-supplied argument) and only `days`-style knobs exposed. -------------


async def test_clinical_tools_wrap_service_layer_with_bound_patient_id(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token, patient_id = await _register(client, "live-toolwiring@example.com")
    await _create_glucose(client, token, _today_at(9), value=133)

    tools = build_patient_tools(patient_id, lambda: _session_cm(db_session))
    tool_by_name = {t.name: t for t in tools}
    assert set(tool_by_name) == {
        "get_today_glucose",
        "get_recent_meals",
        "get_medication_adherence",
        "get_sleep_summary",
        "get_latest_vitals",
        "get_recent_symptoms",
    }

    glucose_result = await tool_by_name["get_today_glucose"].ainvoke({})
    assert glucose_result["count"] == 1
    assert glucose_result["readings"][0]["value"] == 133

    meals_result = await tool_by_name["get_recent_meals"].ainvoke({"days": 3})
    assert meals_result["meals"] == []

    vitals_result = await tool_by_name["get_latest_vitals"].ainvoke({})
    assert vitals_result is None
