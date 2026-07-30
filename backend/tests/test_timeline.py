from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_medication_log import _create_medication
from tests.test_patients import auth_headers, register_patient


async def _create_glucose(
    client: AsyncClient, token: str, event_timestamp: str, value: float = 100, unit: str = "mg_dl"
) -> None:
    response = await client.post(
        "/api/patients/me/glucose",
        json={
            "event_timestamp": event_timestamp,
            "value": value,
            "unit": unit,
            "reading_type": "fasting",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_meal(client: AsyncClient, token: str, event_timestamp: str) -> None:
    response = await client.post(
        "/api/patients/me/meals",
        json={
            "event_timestamp": event_timestamp,
            "meal_type": "breakfast",
            "food_items": "oatmeal",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_exercise(
    client: AsyncClient, token: str, event_timestamp: str, duration_minutes: int = 30
) -> None:
    response = await client.post(
        "/api/patients/me/exercise",
        json={
            "event_timestamp": event_timestamp,
            "exercise_type": "running",
            "duration_minutes": duration_minutes,
            "intensity": "moderate",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_medication_log(
    client: AsyncClient, token: str, medication_id: str, event_timestamp: str, taken: bool
) -> None:
    response = await client.post(
        "/api/patients/me/medication-log",
        json={
            "event_timestamp": event_timestamp,
            "medication_id": medication_id,
            "actual_time": event_timestamp,
            "taken": taken,
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_sleep(client: AsyncClient, token: str, event_timestamp: str) -> None:
    response = await client.post(
        "/api/patients/me/sleep",
        json={
            "event_timestamp": event_timestamp,
            "bedtime": event_timestamp,
            "wake_time": event_timestamp,
            "hours_slept": 7.0,
            "quality": "good",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_stress(client: AsyncClient, token: str, event_timestamp: str) -> None:
    response = await client.post(
        "/api/patients/me/stress",
        json={"event_timestamp": event_timestamp, "stress_level": 5, "mood": "neutral"},
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_symptom(client: AsyncClient, token: str, event_timestamp: str) -> None:
    response = await client.post(
        "/api/patients/me/symptoms",
        json={"event_timestamp": event_timestamp, "symptom_type": "fatigue", "severity": "mild"},
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_vitals(client: AsyncClient, token: str, event_timestamp: str) -> None:
    response = await client.post(
        "/api/patients/me/vitals",
        json={"event_timestamp": event_timestamp, "heart_rate": 70},
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def test_timeline_chronological_ordering_across_mixed_types(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-order@example.com")
    token = reg["tokens"]["access_token"]

    # Created out of chronological order on purpose.
    await _create_exercise(client, token, "2026-03-01T12:00:00Z")
    await _create_glucose(client, token, "2026-03-01T08:00:00Z", value=110)
    await _create_meal(client, token, "2026-03-01T18:00:00Z")

    response = await client.get(
        "/api/patients/me/timeline",
        params={"start": "2026-03-01T00:00:00Z", "end": "2026-03-02T00:00:00Z"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3

    event_types_in_order = [item["event_type"] for item in body]
    assert event_types_in_order == ["meal", "exercise", "glucose"]  # newest first

    timestamps = [item["event_timestamp"] for item in body]
    assert timestamps == sorted(timestamps, reverse=True)

    # Each item's detail is tagged with the same event_type as the envelope,
    # and carries type-appropriate fields — no field-name switch needed.
    glucose_item = body[-1]
    assert glucose_item["detail"]["event_type"] == "glucose"
    assert glucose_item["detail"]["value"] == 110
    meal_item = body[0]
    assert meal_item["detail"]["event_type"] == "meal"
    assert meal_item["detail"]["food_items"] == "oatmeal"


async def test_timeline_filter_by_event_types(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-filtertype@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, "2026-03-01T08:00:00Z")
    await _create_meal(client, token, "2026-03-01T09:00:00Z")
    await _create_exercise(client, token, "2026-03-01T10:00:00Z")

    response = await client.get(
        "/api/patients/me/timeline",
        params={
            "start": "2026-03-01T00:00:00Z",
            "end": "2026-03-02T00:00:00Z",
            "event_types": ["glucose", "meal"],
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    returned_types = {item["event_type"] for item in body}
    assert returned_types == {"glucose", "meal"}
    assert len(body) == 2


async def test_timeline_filter_by_date_range(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-daterange@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, "2026-01-01T08:00:00Z", value=101)
    await _create_glucose(client, token, "2026-01-05T08:00:00Z", value=105)
    await _create_glucose(client, token, "2026-01-10T08:00:00Z", value=110)

    response = await client.get(
        "/api/patients/me/timeline",
        params={"start": "2026-01-03T00:00:00Z", "end": "2026-01-07T00:00:00Z"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["detail"]["value"] == 105


async def test_timeline_defaults_to_today_when_range_omitted(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-defaulttoday@example.com")
    token = reg["tokens"]["access_token"]

    now = datetime.now(UTC)
    await _create_glucose(client, token, now.isoformat(), value=99)
    await _create_glucose(client, token, "2020-01-01T08:00:00Z", value=1)

    response = await client.get("/api/patients/me/timeline", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    values = [item["detail"]["value"] for item in body]
    assert values == [99]


async def test_timeline_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "timelineA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "timelineB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    await _create_glucose(client, token_a, "2026-03-01T08:00:00Z")
    await _create_meal(client, token_a, "2026-03-01T09:00:00Z")

    response = await client.get(
        "/api/patients/me/timeline",
        params={"start": "2026-03-01T00:00:00Z", "end": "2026-03-02T00:00:00Z"},
        headers=auth_headers(token_b),
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_timeline_pagination(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-paging@example.com")
    token = reg["tokens"]["access_token"]

    base = datetime(2026, 3, 1, 8, 0, 0, tzinfo=UTC)
    for i in range(5):
        await _create_glucose(client, token, (base + timedelta(hours=i)).isoformat(), value=100 + i)

    page1 = await client.get(
        "/api/patients/me/timeline",
        params={
            "start": "2026-03-01T00:00:00Z",
            "end": "2026-03-02T00:00:00Z",
            "limit": 2,
            "offset": 0,
        },
        headers=auth_headers(token),
    )
    page2 = await client.get(
        "/api/patients/me/timeline",
        params={
            "start": "2026-03-01T00:00:00Z",
            "end": "2026-03-02T00:00:00Z",
            "limit": 2,
            "offset": 2,
        },
        headers=auth_headers(token),
    )
    assert [item["detail"]["value"] for item in page1.json()] == [104, 103]
    assert [item["detail"]["value"] for item in page2.json()] == [102, 101]


async def test_timeline_bounded_query_count_for_mixed_types(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """The timeline endpoint must not do one detail query per event.

    Seeds one event of each of the 8 types and counts AsyncSession.execute()
    calls made while serving GET /timeline. Measured at 10 for this seed (1
    for get_current_patient's auth lookup + 1 for the HealthEvent page + 8
    batched detail queries, one per distinct type present) — bounded by the
    number of distinct types (8) rather than the number of events, so it
    does not grow with N. Asserting <=12 for headroom against incidental
    changes elsewhere in the request path while still catching an N+1
    regression, which would scale with event count instead.
    """
    reg = await register_patient(client, "timeline-querycount@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    ts = "2026-03-01T08:00:00Z"
    await _create_glucose(client, token, ts)
    await _create_meal(client, token, ts)
    await _create_medication_log(client, token, medication_id, ts, taken=True)
    await _create_exercise(client, token, ts)
    await _create_sleep(client, token, ts)
    await _create_stress(client, token, ts)
    await _create_symptom(client, token, ts)
    await _create_vitals(client, token, ts)

    call_count = 0
    original_execute = AsyncSession.execute

    async def counting_execute(self: AsyncSession, *args: object, **kwargs: object) -> object:
        nonlocal call_count
        call_count += 1
        return await original_execute(self, *args, **kwargs)

    AsyncSession.execute = counting_execute  # type: ignore[method-assign]
    try:
        response = await client.get(
            "/api/patients/me/timeline",
            params={"start": "2026-03-01T00:00:00Z", "end": "2026-03-02T00:00:00Z"},
            headers=auth_headers(token),
        )
    finally:
        AsyncSession.execute = original_execute  # type: ignore[method-assign]

    assert response.status_code == 200
    assert len(response.json()) == 8
    assert call_count <= 12, f"expected a bounded query count, got {call_count} db.execute() calls"


async def test_timeline_summary_rollup_math(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-summary@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    # Two glucose readings on the target day — the later one should win as
    # "latest".
    await _create_glucose(client, token, "2026-04-01T08:00:00Z", value=100)
    await _create_glucose(client, token, "2026-04-01T20:00:00Z", value=140)

    # One taken, one missed medication dose.
    await _create_medication_log(client, token, medication_id, "2026-04-01T09:00:00Z", taken=True)
    await _create_medication_log(client, token, medication_id, "2026-04-01T21:00:00Z", taken=False)

    # Two exercise sessions summing to 50 minutes.
    await _create_exercise(client, token, "2026-04-01T07:00:00Z", duration_minutes=30)
    await _create_exercise(client, token, "2026-04-01T17:00:00Z", duration_minutes=20)

    # One each of the remaining types.
    await _create_meal(client, token, "2026-04-01T12:00:00Z")
    await _create_sleep(client, token, "2026-04-01T06:00:00Z")
    await _create_stress(client, token, "2026-04-01T13:00:00Z")
    await _create_symptom(client, token, "2026-04-01T14:00:00Z")
    await _create_vitals(client, token, "2026-04-01T15:00:00Z")

    # An event on a different day — must not leak into the 2026-04-01 rollup.
    await _create_glucose(client, token, "2026-04-02T08:00:00Z", value=999)

    response = await client.get(
        "/api/patients/me/timeline/summary",
        params={"date": "2026-04-01"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()

    assert body["date"] == "2026-04-01"
    assert body["event_counts"] == {
        "glucose": 2,
        "meal": 1,
        "medication": 2,
        "exercise": 2,
        "sleep": 1,
        "stress": 1,
        "symptom": 1,
        "vitals": 1,
    }
    assert body["total_events"] == 11
    assert body["medications_taken"] == 1
    assert body["medications_missed"] == 1
    assert body["latest_glucose"]["value"] == 140
    assert body["latest_glucose_timestamp"] == "2026-04-01T20:00:00Z"
    assert body["glucose_average_mg_dl"] == 120.0
    assert body["total_exercise_minutes"] == 50
    assert body["average_stress_level"] == 5.0


async def test_timeline_summary_empty_day(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-summary-empty@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.get(
        "/api/patients/me/timeline/summary",
        params={"date": "2026-05-01"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] == 0
    assert body["medications_taken"] == 0
    assert body["medications_missed"] == 0
    assert body["latest_glucose"] is None
    assert body["latest_glucose_timestamp"] is None
    assert body["glucose_average_mg_dl"] is None
    assert body["total_exercise_minutes"] == 0
    assert body["average_stress_level"] is None
    assert all(count == 0 for count in body["event_counts"].values())


async def test_timeline_summary_glucose_average_normalizes_units(client: AsyncClient) -> None:
    reg = await register_patient(client, "timeline-summary-units@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, "2026-04-05T08:00:00Z", value=100, unit="mg_dl")
    await _create_glucose(client, token, "2026-04-05T20:00:00Z", value=10, unit="mmol_l")

    response = await client.get(
        "/api/patients/me/timeline/summary",
        params={"date": "2026-04-05"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    # 10 mmol/L -> ~180.2 mg/dL; average of (100, 180.2) -> ~140.1 mg/dL. If the
    # two units were averaged without normalizing first, this would be very
    # different (e.g. naively averaging 100 and 10 gives 55).
    assert body["glucose_average_mg_dl"] == pytest.approx(140.1, abs=0.1)
    # The "latest" reading keeps its original stored unit/value, not normalized.
    assert body["latest_glucose"]["value"] == 10
    assert body["latest_glucose"]["unit"] == "mmol_l"


async def test_timeline_summary_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "timeline-summaryA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "timeline-summaryB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    await _create_glucose(client, token_a, "2026-04-01T08:00:00Z", value=150)

    response = await client.get(
        "/api/patients/me/timeline/summary",
        params={"date": "2026-04-01"},
        headers=auth_headers(token_b),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["event_counts"]["glucose"] == 0
    assert body["latest_glucose"] is None
