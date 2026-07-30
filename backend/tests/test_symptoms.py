import uuid
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.models.health_event import HealthEvent
from tests.test_patients import auth_headers, register_patient


async def _count_health_events(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(HealthEvent))
    return result.scalar_one()


async def test_symptom_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "symptom-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/symptoms",
        json={
            "event_timestamp": "2026-01-01T14:00:00Z",
            "symptom_type": "fatigue",
            "severity": "moderate",
            "duration_notes": "since morning",
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["symptom_type"] == "fatigue"
    assert body["severity"] == "moderate"

    get_one = await client.get(f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token))
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/symptoms", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/symptoms/{log_id}",
        json={"severity": "severe"},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["severity"] == "severe"
    assert updated.json()["symptom_type"] == "fatigue"

    deleted = await client.delete(
        f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token)
    )
    assert deleted.status_code == 204

    after_delete = await client.get(
        f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token)
    )
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/symptoms", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_symptom_hard_delete_removes_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "symptom-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/symptoms",
        json={
            "event_timestamp": "2026-01-01T14:00:00Z",
            "symptom_type": "dizziness",
            "severity": "mild",
        },
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_symptom_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "symptomA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "symptomB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/symptoms",
        json={
            "event_timestamp": "2026-01-01T14:00:00Z",
            "symptom_type": "nausea",
            "severity": "moderate",
        },
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/symptoms/{log_id}",
            json={"severity": "severe"},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404

    b_list = await client.get("/api/patients/me/symptoms", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(f"/api/patients/me/symptoms/{log_id}", headers=auth_headers(token_a))
    assert a_get.status_code == 200


async def test_create_symptom_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "symptom-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/symptoms",
        json={"event_timestamp": "2026-01-01T14:00:00Z", "severity": "mild"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_symptom_invalid_severity_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "symptom-badseverity@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/symptoms",
        json={
            "event_timestamp": "2026-01-01T14:00:00Z",
            "symptom_type": "fatigue",
            "severity": "extreme",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_symptom_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "symptom-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 14, 0, 0, tzinfo=UTC)
    severities = ["mild", "moderate", "severe", "mild", "moderate"]
    for i in range(5):
        response = await client.post(
            "/api/patients/me/symptoms",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "symptom_type": "fatigue",
                "severity": severities[i],
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/symptoms", headers=auth_headers(token))
    ordered_severities = [log["severity"] for log in all_logs.json()]
    assert ordered_severities == ["moderate", "mild", "severe", "moderate", "mild"]

    page1 = await client.get(
        "/api/patients/me/symptoms", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    assert len(page1.json()) == 2

    ranged = await client.get(
        "/api/patients/me/symptoms",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    assert len(ranged.json()) == 2
