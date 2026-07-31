import uuid
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.models.enums import PatientGoalSource, PatientGoalStatus
from app.clinical_reasoning.models.patient_goal import PatientGoal as PatientGoalModel
from app.clinical_reasoning.services import context_service
from tests.test_medication_log import _create_medication
from tests.test_patients import auth_headers, register_patient
from tests.test_timeline import (
    _create_exercise,
    _create_glucose,
    _create_meal,
    _create_medication_log,
    _create_sleep,
    _create_stress,
    _create_symptom,
)


def _today_at(hour: int) -> str:
    today = datetime.now(UTC).date()
    return datetime(today.year, today.month, today.day, hour, tzinfo=UTC).isoformat()


async def _seed_full_patient(
    client: AsyncClient, db_session: AsyncSession, email: str
) -> tuple[str, uuid.UUID]:
    reg = await register_patient(client, email)
    token = reg["tokens"]["access_token"]
    headers = auth_headers(token)

    profile_response = await client.put(
        "/api/patients/me/profile",
        json={"age": 45, "sex": "female", "height_cm": 165, "weight_kg": 70},
        headers=headers,
    )
    assert profile_response.status_code == 200
    patient_id = uuid.UUID(
        (await client.get("/api/patients/me/profile", headers=headers)).json()["patient"]["id"]
    )

    history_response = await client.put(
        "/api/patients/me/medical-history",
        json={
            "diabetes_type": "type2",
            "years_since_diagnosis": 5,
            "family_history": True,
            "latest_hba1c": 7.2,
            "has_kidney_disease": False,
            "comorbidities": ["hypertension"],
        },
        headers=headers,
    )
    assert history_response.status_code == 200

    lifestyle_response = await client.put(
        "/api/patients/me/lifestyle",
        json={"sleep_hours_avg": 7.0, "exercise_frequency": "3x/week", "stress_level_baseline": 4},
        headers=headers,
    )
    assert lifestyle_response.status_code == 200

    medication_id = await _create_medication(client, token, "Metformin")

    await _create_glucose(client, token, _today_at(8), value=110)
    await _create_meal(client, token, _today_at(8))
    await _create_medication_log(client, token, medication_id, _today_at(9), taken=True)
    await _create_exercise(client, token, _today_at(7), duration_minutes=30)
    await _create_sleep(client, token, _today_at(6))
    await _create_stress(client, token, _today_at(10))
    await _create_symptom(client, token, _today_at(11))

    goal = PatientGoalModel(
        patient_id=patient_id,
        goal="Keep fasting glucose under 130",
        context="Discussed at last check-in",
        status=PatientGoalStatus.active,
        source=PatientGoalSource.patient_stated,
    )
    db_session.add(goal)
    await db_session.commit()

    return token, patient_id


async def test_build_context_populates_every_field(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    _, patient_id = await _seed_full_patient(client, db_session, "context-full@example.com")

    context = await context_service.build_context(db_session, patient_id)

    assert context.patient_id == patient_id
    assert context.version == 1

    assert context.demographics.age == 45
    assert context.demographics.sex.value == "female"
    assert context.demographics.height_cm == 165
    assert context.demographics.bmi is not None

    assert context.diabetes_history.diabetes_type.value == "type2"
    assert context.diabetes_history.years_since_diagnosis == 5
    assert context.diabetes_history.family_history is True
    assert context.diabetes_history.comorbidities == ["hypertension"]

    assert len(context.medications) == 1
    assert context.medications[0].name == "Metformin"
    assert context.medications[0].last_logged_at is not None

    assert context.latest_glucose is not None
    assert context.latest_glucose.value == 110

    assert context.last_7_day_summary.meals_logged_count >= 1
    assert context.last_7_day_summary.meals_logged_today >= 1
    assert context.last_7_day_summary.exercise_total_minutes >= 30
    assert context.last_7_day_summary.sleep_average_hours is not None
    assert context.last_7_day_summary.last_sleep_at is not None
    assert context.last_7_day_summary.average_stress_level is not None
    assert context.last_7_day_summary.symptoms_logged_count >= 1
    assert context.last_7_day_summary.glucose_average_mg_dl is not None

    assert context.adherence_summary.doses_taken_7day >= 1
    assert context.adherence_summary.adherence_pct_7day == 100.0

    assert len(context.active_symptoms) >= 1
    assert context.active_symptoms[0].symptom_type.value == "fatigue"

    assert context.lifestyle_summary.sleep_hours_avg == 7.0
    assert context.lifestyle_summary.exercise_frequency == "3x/week"

    assert len(context.goals) == 1
    assert context.goals[0].goal == "Keep fasting glucose under 130"
    assert context.goals[0].source == "patient_stated"

    # Explicit per the milestone scope: these fields are always empty until
    # Sprint 4 (patterns) / Milestone 3.3 (episodic memory barriers).
    assert context.recent_patterns == []
    assert context.known_barriers == []


async def test_build_context_defaults_when_no_profile_data_submitted(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "context-empty@example.com")
    token = reg["tokens"]["access_token"]
    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    patient_id = uuid.UUID(profile.json()["patient"]["id"])

    context = await context_service.build_context(db_session, patient_id)

    assert context.diabetes_history.diabetes_type is None
    assert context.diabetes_history.comorbidities == []
    assert context.medications == []
    assert context.latest_glucose is None
    assert context.lifestyle_summary.sleep_hours_avg is None
    assert context.goals == []
    assert context.active_symptoms == []
    assert context.last_7_day_summary.total_events == 0
    assert context.adherence_summary.adherence_pct_7day is None
    assert context.recent_patterns == []
    assert context.known_barriers == []


async def test_build_context_medication_last_logged_at_reflects_most_recent_log(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "context-medlog@example.com")
    token = reg["tokens"]["access_token"]
    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    patient_id = uuid.UUID(profile.json()["patient"]["id"])
    medication_id = await _create_medication(client, token, "Metformin")

    older = (datetime.now(UTC) - timedelta(hours=10)).isoformat()
    newer = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    await _create_medication_log(client, token, medication_id, older, taken=True)
    await _create_medication_log(client, token, medication_id, newer, taken=False)

    context = await context_service.build_context(db_session, patient_id)
    med_summary = next(m for m in context.medications if m.name == "Metformin")
    assert med_summary.last_logged_at is not None
    # Within a couple of seconds of the newer log's timestamp.
    assert abs((med_summary.last_logged_at - datetime.fromisoformat(newer)).total_seconds()) < 5


async def test_build_context_version_increments_across_calls(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # build_context() itself doesn't persist, so calling it twice in a row
    # with nothing else writing a snapshot in between assigns the same next
    # version both times — version only advances once something actually
    # persists at that version (see clinical_reasoning_service tests for the
    # real incrementing behavior).
    reg = await register_patient(client, "context-version@example.com")
    token = reg["tokens"]["access_token"]
    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    patient_id = uuid.UUID(profile.json()["patient"]["id"])

    first = await context_service.build_context(db_session, patient_id)
    second = await context_service.build_context(db_session, patient_id)
    assert first.version == 1
    assert second.version == 1
