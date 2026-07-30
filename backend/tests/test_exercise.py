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


async def test_exercise_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "exercise-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/exercise",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "exercise_type": "running",
            "duration_minutes": 30,
            "intensity": "moderate",
            "calories_burned": 250,
            "heart_rate_avg": 140,
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["exercise_type"] == "running"
    assert body["intensity"] == "moderate"

    get_one = await client.get(f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token))
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/exercise", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/exercise/{log_id}",
        json={"duration_minutes": 45},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["duration_minutes"] == 45
    assert updated.json()["exercise_type"] == "running"

    deleted = await client.delete(
        f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token)
    )
    assert deleted.status_code == 204

    after_delete = await client.get(
        f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token)
    )
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/exercise", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_exercise_hard_delete_removes_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "exercise-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/exercise",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "exercise_type": "swimming",
            "duration_minutes": 20,
            "intensity": "light",
        },
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_exercise_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "exerciseA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "exerciseB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/exercise",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "exercise_type": "cycling",
            "duration_minutes": 40,
            "intensity": "vigorous",
        },
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/exercise/{log_id}",
            json={"duration_minutes": 5},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404

    b_list = await client.get("/api/patients/me/exercise", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(f"/api/patients/me/exercise/{log_id}", headers=auth_headers(token_a))
    assert a_get.status_code == 200


async def test_create_exercise_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "exercise-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/exercise",
        json={"event_timestamp": "2026-01-01T08:00:00Z", "exercise_type": "yoga"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_exercise_invalid_intensity_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "exercise-badintensity@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/exercise",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "exercise_type": "running",
            "duration_minutes": 30,
            "intensity": "extreme",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_exercise_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "exercise-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/exercise",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "exercise_type": "running",
                "duration_minutes": 20 + i,
                "intensity": "moderate",
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/exercise", headers=auth_headers(token))
    durations = [log["duration_minutes"] for log in all_logs.json()]
    assert durations == [24, 23, 22, 21, 20]

    page1 = await client.get(
        "/api/patients/me/exercise", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    assert [log["duration_minutes"] for log in page1.json()] == [24, 23]

    ranged = await client.get(
        "/api/patients/me/exercise",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    ranged_durations = sorted(log["duration_minutes"] for log in ranged.json())
    assert ranged_durations == [22, 23]
