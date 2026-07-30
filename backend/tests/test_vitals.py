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


async def test_vitals_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "vitals-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/vitals",
        json={
            "event_timestamp": "2026-01-01T07:00:00Z",
            "weight_kg": 70.5,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 72,
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["weight_kg"] == 70.5
    assert body["blood_pressure_systolic"] == 120

    get_one = await client.get(f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token))
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/vitals", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/vitals/{log_id}",
        json={"weight_kg": 71.0},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["weight_kg"] == 71.0
    assert updated.json()["heart_rate"] == 72

    deleted = await client.delete(f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token))
    assert deleted.status_code == 204

    after_delete = await client.get(
        f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token)
    )
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/vitals", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_vitals_hard_delete_removes_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "vitals-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/vitals",
        json={"event_timestamp": "2026-01-01T07:00:00Z", "weight_kg": 65.0},
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_vitals_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "vitalsA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "vitalsB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/vitals",
        json={"event_timestamp": "2026-01-01T07:00:00Z", "heart_rate": 90},
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/vitals/{log_id}",
            json={"heart_rate": 1},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404

    b_list = await client.get("/api/patients/me/vitals", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(f"/api/patients/me/vitals/{log_id}", headers=auth_headers(token_a))
    assert a_get.status_code == 200


async def test_create_vitals_missing_event_timestamp_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "vitals-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/vitals",
        json={"weight_kg": 70.0},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_vitals_invalid_field_type_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "vitals-badtype@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/vitals",
        json={"event_timestamp": "2026-01-01T07:00:00Z", "blood_pressure_systolic": "high"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_vitals_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "vitals-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 7, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/vitals",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "weight_kg": 70.0 + i,
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/vitals", headers=auth_headers(token))
    weights = [log["weight_kg"] for log in all_logs.json()]
    assert weights == [74.0, 73.0, 72.0, 71.0, 70.0]

    page1 = await client.get(
        "/api/patients/me/vitals", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    assert [log["weight_kg"] for log in page1.json()] == [74.0, 73.0]

    ranged = await client.get(
        "/api/patients/me/vitals",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    ranged_weights = sorted(log["weight_kg"] for log in ranged.json())
    assert ranged_weights == [72.0, 73.0]
