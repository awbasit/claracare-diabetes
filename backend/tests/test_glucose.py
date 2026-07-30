import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.glucose.service import mg_dl_to_mmol_l, mmol_l_to_mg_dl
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent
from app.health_events.services import health_event_service
from tests.test_patients import auth_headers, register_patient


async def _count_health_events(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(HealthEvent))
    return result.scalar_one()


def test_glucose_unit_conversion_helpers() -> None:
    assert mg_dl_to_mmol_l(180) == pytest.approx(9.99, rel=1e-2)
    assert mmol_l_to_mg_dl(10) == pytest.approx(180.18, rel=1e-2)


async def test_glucose_crud_round_trip(client: AsyncClient) -> None:
    reg = await register_patient(client, "glucose-crud@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/glucose",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "value": 110,
            "unit": "mg_dl",
            "reading_type": "fasting",
            "notes": "felt fine",
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    body = create.json()
    reading_id = body["id"]
    assert body["value"] == 110
    assert body["unit"] == "mg_dl"
    assert body["reading_type"] == "fasting"
    assert body["notes"] == "felt fine"
    assert body["manually_entered"] is True
    assert body["value_mg_dl"] == 110  # already in mg_dl, no conversion needed

    get_one = await client.get(
        f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token)
    )
    assert get_one.status_code == 200
    assert get_one.json()["id"] == reading_id

    listed = await client.get("/api/patients/me/glucose", headers=auth_headers(token))
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/glucose/{reading_id}",
        json={"value": 95, "notes": "rechecked"},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["value"] == 95
    assert updated.json()["notes"] == "rechecked"
    assert updated.json()["reading_type"] == "fasting"  # untouched field preserved

    deleted = await client.delete(
        f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token)
    )
    assert deleted.status_code == 204

    after_delete = await client.get(
        f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token)
    )
    assert after_delete.status_code == 404

    listed_after = await client.get("/api/patients/me/glucose", headers=auth_headers(token))
    assert listed_after.json() == []


async def test_glucose_hard_delete_removes_row(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "glucose-harddelete@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/glucose",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "value": 100,
            "unit": "mg_dl",
            "reading_type": "fasting",
        },
        headers=auth_headers(token),
    )
    reading_id = create.json()["id"]

    await client.delete(f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token))

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.id == uuid.UUID(reading_id))
    )
    assert result.scalar_one_or_none() is None


async def test_glucose_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "glucoseA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "glucoseB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/glucose",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "value": 100,
            "unit": "mg_dl",
            "reading_type": "fasting",
        },
        headers=auth_headers(token_a),
    )
    reading_id = create.json()["id"]

    steal_get = await client.get(
        f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token_b)
    )
    assert steal_get.status_code == 404

    steal_update = await client.put(
        f"/api/patients/me/glucose/{reading_id}",
        json={"value": 999},
        headers=auth_headers(token_b),
    )
    assert steal_update.status_code == 404

    steal_delete = await client.delete(
        f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token_b)
    )
    assert steal_delete.status_code == 404

    b_list = await client.get("/api/patients/me/glucose", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_get = await client.get(
        f"/api/patients/me/glucose/{reading_id}", headers=auth_headers(token_a)
    )
    assert a_get.status_code == 200


async def test_create_glucose_missing_required_field_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "glucose-missingfield@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/glucose",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "unit": "mg_dl",
            "reading_type": "fasting",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_glucose_invalid_unit_returns_422_without_orphan(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    reg = await register_patient(client, "glucose-badunit@example.com")
    token = reg["tokens"]["access_token"]

    before = await _count_health_events(db_session)

    response = await client.post(
        "/api/patients/me/glucose",
        json={
            "event_timestamp": "2026-01-01T08:00:00Z",
            "value": 100,
            "unit": "not-a-real-unit",
            "reading_type": "fasting",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 422

    after = await _count_health_events(db_session)
    assert after == before


async def test_create_event_with_unregistered_event_type_fails_without_orphan(
    db_session: AsyncSession,
) -> None:
    patient_id = uuid.uuid4()

    # Every EventType member now has a registered detail service (Prompt 2
    # filled in the rest), so there's no naturally-unregistered type left to
    # exercise this path with. Simulate one by briefly un-registering glucose.
    saved_service = health_event_service._detail_services.pop(EventType.glucose)
    try:
        with pytest.raises(ValueError, match="No detail service registered"):
            await health_event_service.create_event(
                db_session,
                patient_id=patient_id,
                event_type=EventType.glucose,
                event_timestamp=datetime.now(UTC),
                notes=None,
                detail_data={},
            )
    finally:
        health_event_service._detail_services[EventType.glucose] = saved_service

    result = await db_session.execute(
        select(HealthEvent).where(HealthEvent.patient_id == patient_id)
    )
    assert result.scalar_one_or_none() is None


async def test_glucose_date_range_and_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "glucose-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)
    for i in range(5):
        response = await client.post(
            "/api/patients/me/glucose",
            json={
                "event_timestamp": (base + timedelta(days=i)).isoformat(),
                "value": 100 + i,
                "unit": "mg_dl",
                "reading_type": "fasting",
            },
            headers=auth_headers(token),
        )
        assert response.status_code == 201

    all_readings = await client.get("/api/patients/me/glucose", headers=auth_headers(token))
    values = [r["value"] for r in all_readings.json()]
    assert values == [104, 103, 102, 101, 100]  # reverse-chronological by default

    page1 = await client.get(
        "/api/patients/me/glucose", params={"limit": 2, "offset": 0}, headers=auth_headers(token)
    )
    page2 = await client.get(
        "/api/patients/me/glucose", params={"limit": 2, "offset": 2}, headers=auth_headers(token)
    )
    assert [r["value"] for r in page1.json()] == [104, 103]
    assert [r["value"] for r in page2.json()] == [102, 101]

    ranged = await client.get(
        "/api/patients/me/glucose",
        params={
            "start": (base + timedelta(days=2)).isoformat(),
            "end": (base + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers(token),
    )
    ranged_values = sorted(r["value"] for r in ranged.json())
    assert ranged_values == [102, 103]
