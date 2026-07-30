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


async def _create_medication(client: AsyncClient, token: str, name: str = "Metformin") -> str:
    response = await client.post(
        "/api/patients/me/medications", json={"name": name}, headers=auth_headers(token)
    )
    assert response.status_code == 201
    result: str = response.json()["id"]
    return result


async def test_medication_log_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "medlog-crud@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    create = await client.post(
        "/api/patients/me/medication-log",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "medication_id": medication_id,
            "actual_time": "2026-01-01T08:05:00Z",
            "taken": True,
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["medication_id"] == medication_id
    assert body["taken"] is True

    get_one = await client.get(
        f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token)
    )
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/medication-log", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/medication-log/{log_id}",
        json={"taken": False, "missed_reason": "forgot"},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["taken"] is False
    assert updated.json()["missed_reason"] == "forgot"

    deleted = await client.delete(
        f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token)
    )
    assert deleted.status_code == 204

    after_delete = await client.get(
        f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token)
    )
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/medication-log", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_medication_log_hard_delete_removes_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "medlog-harddelete@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    create = await client.post(
        "/api/patients/me/medication-log",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "medication_id": medication_id,
            "actual_time": "2026-01-01T08:05:00Z",
            "taken": True,
        },
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_medication_log_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "medlogA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    medication_id = await _create_medication(client, token_a)
    patient_b = await register_patient(client, "medlogB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/medication-log",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "medication_id": medication_id,
            "actual_time": "2026-01-01T08:05:00Z",
            "taken": True,
        },
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/medication-log/{log_id}",
            json={"taken": False},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(
            f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token_b)
        )
    ).status_code == 404

    b_list = await client.get("/api/patients/me/medication-log", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(
        f"/api/patients/me/medication-log/{log_id}", headers=auth_headers(token_a)
    )
    assert a_get.status_code == 200


async def test_medication_log_cannot_reference_another_patients_medication(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    patient_a = await register_patient(client, "medlog-ownerA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    medication_id_a = await _create_medication(client, token_a)

    patient_b = await register_patient(client, "medlog-ownerB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/medication-log",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "medication_id": medication_id_a,
            "actual_time": "2026-01-01T08:05:00Z",
            "taken": True,
        },
        headers=auth_headers(token_b),
    )
    assert response.status_code == 404

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_medication_log_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "medlog-missingfield@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/medication-log",
        json={"event_timestamp": "2026-01-01T08:00:00Z", "medication_id": medication_id},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_medication_log_unknown_medication_id_returns_404_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "medlog-unknownmed@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/medication-log",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "medication_id": str(uuid.uuid4()),
            "actual_time": "2026-01-01T08:05:00Z",
            "taken": True,
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 404

    after = await _count_health_events(db_session)
    assert after == before


async def test_medication_log_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "medlog-paging@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    base = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/medication-log",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "medication_id": medication_id,
                "actual_time": (base + timedelta(days=i)).isoformat(),
                "taken": True,
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/medication-log", headers=auth_headers(token))
    assert len(all_logs.json()) == 5

    page1 = await client.get(
        "/api/patients/me/medication-log",
        params={"limit": 2, "offset": 0},
        headers=auth_headers(token),
    )
    assert len(page1.json()) == 2

    ranged = await client.get(
        "/api/patients/me/medication-log",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    assert len(ranged.json()) == 2
