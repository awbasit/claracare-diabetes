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


async def test_meal_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "meal-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/meals",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "meal_type": "breakfast",
            "food_items": "oatmeal and eggs",
            "estimated_carbs_g": 45.5,
            "estimated_calories": 350,
            "portion_size": "1 bowl",
            "drink": "water",
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    log_id = body["id"]
    assert body["meal_type"] == "breakfast"
    assert body["food_items"] == "oatmeal and eggs"
    assert body["estimated_carbs_g"] == 45.5

    get_one = await client.get(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token))
    assert get_one.status_code == 200

    listed = await client.get("/api/patients/me/meals", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/meals/{log_id}",
        json={"estimated_calories": 400},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["estimated_calories"] == 400
    assert updated.json()["meal_type"] == "breakfast"  # untouched field preserved

    deleted = await client.delete(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token))
    assert deleted.status_code == 204

    after_delete = await client.get(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token))
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/meals", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_meal_hard_delete_removes_row(client: AsyncClient, db_session: AsyncSession) -> None:
    reg = await register_patient(client, "meal-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/meals",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "meal_type": "lunch",
            "food_items": "rice and beans",
        },
        headers=auth_headers(token),
    )
    log_id = create.json()["id"]

    await client.delete(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(log_id))
    )
    assert result.scalar_one_or_none() is None


async def test_meal_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "mealA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "mealB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/meals",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "meal_type": "dinner",
            "food_items": "grilled chicken",
        },
        headers=auth_headers(token_a),
    )
    log_id = create.json()["id"]

    assert (
        await client.get(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404
    assert (
        await client.put(
            f"/api/patients/me/meals/{log_id}",
            json={"food_items": "stolen"},
            headers=auth_headers(token_b),
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token_b))
    ).status_code == 404

    b_list = await client.get("/api/patients/me/meals", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(f"/api/patients/me/meals/{log_id}", headers=auth_headers(token_a))
    assert a_get.status_code == 200


async def test_create_meal_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "meal-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/meals",
        json={"event_timestamp": "2026-01-01T08:00:00Z", "meal_type": "snack"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_meal_invalid_meal_type_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "meal-badtype@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/meals",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "meal_type": "brunch",
            "food_items": "pancakes",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_meal_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "meal-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/meals",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "meal_type": "breakfast",
                "food_items": f"meal {i}",
                "estimated_calories": 300 + i,
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_logs = await client.get("/api/patients/me/meals", headers=auth_headers(token))
    calories = [log["estimated_calories"] for log in all_logs.json()]
    assert calories == [304, 303, 302, 301, 300]

    page1 = await client.get(
        "/api/patients/me/meals", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    page2 = await client.get(
        "/api/patients/me/meals", params={"limit": 2, "offset": 2}, headers=auth_headers(token)
    )
    assert [log["estimated_calories"] for log in page1.json()] == [304, 303]
    assert [log["estimated_calories"] for log in page2.json()] == [302, 301]

    ranged = await client.get(
        "/api/patients/me/meals",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    ranged_calories = sorted(log["estimated_calories"] for log in ranged.json())
    assert ranged_calories == [302, 303]
