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


async def test_sleep_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "sleep-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/sleep",
        json={
            "event_timestamp": "2026-01-01T22:00:00Z",
            "bedtime": "2026-01-01T22:00:00Z",
            "wake_time": "2026-01-02T06:00:00Z",
            "hours_slept": 8.0,
            "quality": "good",
            "night_awakenings": 1,
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["quality"] == "good"
    assert body["hours_slept"] == 8.0

    get_one = await client.get(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token))
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/sleep", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/sleep/{log_id}",
        json={"hours_slept": 7.5},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["hours_slept"] == 7.5
    assert updated.json()["quality"] == "good"

    deleted = await client.delete(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token))
    assert deleted.status_code == 204

    after_delete = await client.get(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token))
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/sleep", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_sleep_hard_delete_removes_row(client: AsyncClient, db_session: AsyncSession) -> None:
    reg = await register_patient(client, "sleep-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/sleep",
        json={
            "event_timestamp": "2026-01-01T22:00:00Z",
            "bedtime": "2026-01-01T22:00:00Z",
            "wake_time": "2026-01-02T06:00:00Z",
            "hours_slept": 8.0,
            "quality": "fair",
        },
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_sleep_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "sleepA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "sleepB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/sleep",
        json={
            "event_timestamp": "2026-01-01T22:00:00Z",
            "bedtime": "2026-01-01T22:00:00Z",
            "wake_time": "2026-01-02T06:00:00Z",
            "hours_slept": 8.0,
            "quality": "excellent",
        },
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/sleep/{log_id}",
            json={"hours_slept": 1.0},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404

    b_list = await client.get("/api/patients/me/sleep", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(f"/api/patients/me/sleep/{log_id}", headers=auth_headers(token_a))
    assert a_get.status_code == 200


async def test_create_sleep_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "sleep-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/sleep",
        json={"event_timestamp": "2026-01-01T22:00:00Z", "bedtime": "2026-01-01T22:00:00Z"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_sleep_invalid_quality_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "sleep-badquality@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/sleep",
        json={
            "event_timestamp": "2026-01-01T22:00:00Z",
            "bedtime": "2026-01-01T22:00:00Z",
            "wake_time": "2026-01-02T06:00:00Z",
            "hours_slept": 8.0,
            "quality": "terrible",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_sleep_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "sleep-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 22, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/sleep",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "bedtime": (base + timedelta(days=i)).isoformat(),
                "wake_time": (base + timedelta(days=i, hours=8)).isoformat(),
                "hours_slept": 8.0 + i,
                "quality": "good",
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/sleep", headers=auth_headers(token))
    hours = [log["hours_slept"] for log in all_logs.json()]
    assert hours == [12.0, 11.0, 10.0, 9.0, 8.0]

    page1 = await client.get(
        "/api/patients/me/sleep", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    assert [log["hours_slept"] for log in page1.json()] == [12.0, 11.0]

    ranged = await client.get(
        "/api/patients/me/sleep",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    ranged_hours = sorted(log["hours_slept"] for log in ranged.json())
    assert ranged_hours == [10.0, 11.0]
