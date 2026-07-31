import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.clinical_reasoning.services import clinical_reasoning_service
from app.clinical_reasoning.services.rules import _MEAL_CHECKPOINTS_HOUR
from tests.test_patients import auth_headers, register_patient
from tests.test_timeline import _create_glucose


def _expected_meal_finding_now() -> bool:
    """Mirrors MealRule's own checkpoint logic so the orchestration test's
    assertions are correct no matter what time of day the suite runs —
    generate_assessment() always uses real wall-clock time internally.
    """
    hour = datetime.now(UTC).hour
    expected_by_now = sum(1 for checkpoint in _MEAL_CHECKPOINTS_HOUR if hour >= checkpoint)
    return expected_by_now > 0


async def test_generate_assessment_hand_computed_for_fresh_patient(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "reasoning-fresh@example.com")
    token = reg["tokens"]["access_token"]
    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    patient_id = uuid.UUID(profile.json()["patient"]["id"])

    assessment = await clinical_reasoning_service.generate_assessment(db_session, patient_id)

    assert assessment.version == 1
    assert assessment.context_version == 1
    assert assessment.contradictions == []  # nothing produces these in Milestone 3.1

    findings_by_type = {f.event_type: f for f in assessment.missing_information}
    assert "glucose" in findings_by_type
    assert findings_by_type["glucose"].severity == "medium"  # oral_or_none regimen, no medications
    assert "sleep" in findings_by_type
    assert findings_by_type["sleep"].severity == "low"
    assert ("meal" in findings_by_type) == _expected_meal_finding_now()
    # No high-severity gaps for a med-free, oral-regimen patient -> no derived uncertainties.
    assert assessment.uncertainties == []

    quality = assessment.data_quality.by_type
    # No active medications -> nothing expected -> trivially complete.
    assert quality["medication"].completeness == 1.0
    assert quality["medication"].freshness == 0.0
    # No glucose ever logged.
    assert quality["glucose"].completeness == 0.0
    assert quality["glucose"].freshness == 0.0
    assert quality["glucose"].consistency == 1.0
    # Freshly registered -> cold start for baseline calculators.
    assert quality["meal"].reliability == pytest.approx(0.6)
    assert quality["sleep"].reliability == pytest.approx(0.6)
    assert quality["stress"].reliability == pytest.approx(0.6)
    assert quality["exercise"].coverage_label == "unknown"
    assert quality["symptom"].coverage_label == "unknown"

    overall = assessment.data_quality.overall
    # Hand-computed simple average across all 7 types (§12 open item 1):
    # completeness = (1.0 + 0*6) / 7; freshness = 0/7; consistency = 7*1.0/7;
    # reliability = (0.9*4 + 0.6*3) / 7.
    assert overall.completeness == pytest.approx(1 / 7, abs=0.01)
    assert overall.freshness == 0.0
    assert overall.consistency == 1.0
    assert overall.reliability == pytest.approx((0.9 * 4 + 0.6 * 3) / 7, abs=0.01)
    assert overall.coverage_label is None


async def test_generate_assessment_persists_and_round_trips_through_the_api(
    client: AsyncClient,
) -> None:
    reg = await register_patient(client, "reasoning-persist@example.com")
    token = reg["tokens"]["access_token"]
    headers = auth_headers(token)

    create_response = await client.post("/api/patients/me/context/snapshot", headers=headers)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["version"] == 1

    latest_response = await client.get("/api/patients/me/context/snapshot/latest", headers=headers)
    assert latest_response.status_code == 200
    assert latest_response.json()["version"] == 1
    assert latest_response.json()["patient_context"]["version"] == 1

    version_response = await client.get("/api/patients/me/context/snapshot/1", headers=headers)
    assert version_response.status_code == 200
    assert version_response.json() == latest_response.json()


async def test_versioning_is_sequential_and_old_versions_are_immutable(client: AsyncClient) -> None:
    reg = await register_patient(client, "reasoning-versioning@example.com")
    token = reg["tokens"]["access_token"]
    headers = auth_headers(token)

    first = await client.post("/api/patients/me/context/snapshot", headers=headers)
    assert first.json()["version"] == 1
    assert first.json()["patient_context"]["latest_glucose"] is None

    await _create_glucose(client, token, datetime.now(UTC).isoformat(), value=123)

    second = await client.post("/api/patients/me/context/snapshot", headers=headers)
    assert second.json()["version"] == 2
    assert second.json()["patient_context"]["latest_glucose"]["value"] == 123

    # The old version must still reflect the world as it was when generated
    # — not silently pick up the glucose reading logged afterward.
    old_again = await client.get("/api/patients/me/context/snapshot/1", headers=headers)
    assert old_again.json()["version"] == 1
    assert old_again.json()["patient_context"]["latest_glucose"] is None

    latest = await client.get("/api/patients/me/context/snapshot/latest", headers=headers)
    assert latest.json()["version"] == 2


async def test_get_latest_snapshot_404_before_any_snapshot_exists(client: AsyncClient) -> None:
    reg = await register_patient(client, "reasoning-nolatest@example.com")
    token = reg["tokens"]["access_token"]
    response = await client.get(
        "/api/patients/me/context/snapshot/latest", headers=auth_headers(token)
    )
    assert response.status_code == 404


async def test_get_specific_version_404_when_it_does_not_exist(client: AsyncClient) -> None:
    reg = await register_patient(client, "reasoning-noversion@example.com")
    token = reg["tokens"]["access_token"]
    headers = auth_headers(token)
    await client.post("/api/patients/me/context/snapshot", headers=headers)

    response = await client.get("/api/patients/me/context/snapshot/99", headers=headers)
    assert response.status_code == 404


async def test_cross_patient_isolation_on_all_snapshot_endpoints(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "reasoningA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "reasoningB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    await client.post("/api/patients/me/context/snapshot", headers=auth_headers(token_a))

    # B has never generated a snapshot and must not see A's.
    latest_b = await client.get(
        "/api/patients/me/context/snapshot/latest", headers=auth_headers(token_b)
    )
    assert latest_b.status_code == 404

    version_b = await client.get(
        "/api/patients/me/context/snapshot/1", headers=auth_headers(token_b)
    )
    assert version_b.status_code == 404


async def test_snapshot_endpoints_require_authentication(client: AsyncClient) -> None:
    assert (await client.post("/api/patients/me/context/snapshot")).status_code == 401
    assert (await client.get("/api/patients/me/context/snapshot/latest")).status_code == 401
    assert (await client.get("/api/patients/me/context/snapshot/1")).status_code == 401
