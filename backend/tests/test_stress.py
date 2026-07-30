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


async def test_stress_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "stress-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/stress",
        json={
            "event_timestamp": "2026-01-01T18:00:00Z",
            "stress_level": 5,
            "mood": "neutral",
            "energy_level": 6,
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["stress_level"] == 5
    assert body["mood"] == "neutral"

    get_one = await client.get(f"/api/patients/me/stress/{log_id}", headers=auth_headers(token))
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/stress", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/stress/{log_id}",
        json={"stress_level": 8},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["stress_level"] == 8
    assert updated.json()["mood"] == "neutral"

    deleted = await client.delete(f"/api/patients/me/stress/{log_id}", headers=auth_headers(token))
    assert deleted.status_code == 204

    after_delete = await client.get(
        f"/api/patients/me/stress/{log_id}", headers=auth_headers(token)
    )
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/stress", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_stress_hard_delete_removes_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "stress-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/stress",
        json={"event_timestamp": "2026-01-01T18:00:00Z", "stress_level": 3, "mood": "good"},
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/stress/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_stress_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "stressA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "stressB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/stress",
        json={"event_timestamp": "2026-01-01T18:00:00Z", "stress_level": 7, "mood": "high"},
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/stress/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/stress/{log_id}",
            json={"stress_level": 1},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/patients/me/stress/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404

    b_list = await client.get("/api/patients/me/stress", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(f"/api/patients/me/stress/{log_id}", headers=auth_headers(token_a))
    assert a_get.status_code == 200


async def test_create_stress_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "stress-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/stress",
        json={"event_timestamp": "2026-01-01T18:00:00Z", "mood": "neutral"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_stress_out_of_range_level_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "stress-outofrange@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/stress",
        json={"event_timestamp": "2026-01-01T18:00:00Z", "stress_level": 11, "mood": "neutral"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_stress_invalid_mood_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "stress-badmood@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/stress",
        json={"event_timestamp": "2026-01-01T18:00:00Z", "stress_level": 5, "mood": "ecstatic"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_stress_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "stress-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 18, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/stress",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "stress_level": i + 1,
                "mood": "neutral",
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/stress", headers=auth_headers(token))
    levels = [log["stress_level"] for log in all_logs.json()]
    assert levels == [5, 4, 3, 2, 1]

    page1 = await client.get(
        "/api/patients/me/stress", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    assert [log["stress_level"] for log in page1.json()] == [5, 4]

    ranged = await client.get(
        "/api/patients/me/stress",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    ranged_levels = sorted(log["stress_level"] for log in ranged.json())
    assert ranged_levels == [3, 4]
