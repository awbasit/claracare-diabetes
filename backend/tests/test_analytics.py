from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from tests.test_medication_log import _create_medication
from tests.test_patients import auth_headers, register_patient
from tests.test_timeline import (
    _create_exercise,
    _create_glucose,
    _create_medication_log,
)


def _today_at(hour: int) -> str:
    today = datetime.now(UTC).date()
    return datetime(today.year, today.month, today.day, hour, tzinfo=UTC).isoformat()


async def _create_meal_with_carbs(
    client: AsyncClient, token: str, event_timestamp: str, estimated_carbs_g: float | None
) -> None:
    response = await client.post(
        "/api/patients/me/meals",
        json={
            "event_timestamp": event_timestamp,
            "meal_type": "breakfast",
            "food_items": "oatmeal",
            "estimated_carbs_g": estimated_carbs_g,
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_sleep_with(
    client: AsyncClient, token: str, event_timestamp: str, hours_slept: float, quality: str
) -> None:
    response = await client.post(
        "/api/patients/me/sleep",
        json={
            "event_timestamp": event_timestamp,
            "bedtime": event_timestamp,
            "wake_time": event_timestamp,
            "hours_slept": hours_slept,
            "quality": quality,
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def _create_stress_with(
    client: AsyncClient,
    token: str,
    event_timestamp: str,
    stress_level: int,
    energy_level: int | None = None,
) -> None:
    response = await client.post(
        "/api/patients/me/stress",
        json={
            "event_timestamp": event_timestamp,
            "stress_level": stress_level,
            "mood": "neutral",
            "energy_level": energy_level,
        },
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


async def _create_vitals_with(
    client: AsyncClient,
    token: str,
    event_timestamp: str,
    weight_kg: float | None = None,
    systolic: int | None = None,
    diastolic: int | None = None,
) -> None:
    response = await client.post(
        "/api/patients/me/vitals",
        json={
            "event_timestamp": event_timestamp,
            "weight_kg": weight_kg,
            "blood_pressure_systolic": systolic,
            "blood_pressure_diastolic": diastolic,
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201


async def test_trends_week_has_seven_points_for_every_type(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-week@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, _today_at(8), value=100)

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["period"] == "week"
    assert body["glucose_unit"] == "mg_dl"
    for key in (
        "glucose",
        "meals",
        "medication",
        "exercise",
        "sleep",
        "stress",
        "symptoms",
        "vitals",
    ):
        assert len(body[key]) == 7, key

    today = datetime.now(UTC).date()
    assert body["glucose"][-1]["date"] == today.isoformat()
    assert body["glucose"][-1]["average"] == 100
    assert body["glucose"][-1]["count"] == 1
    assert all(p["count"] == 0 and p["average"] is None for p in body["glucose"][:-1])


async def test_trends_month_has_thirty_points_for_every_type(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-month@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "month"}, headers=auth_headers(token)
    )
    assert response.status_code == 200
    body = response.json()
    for key in (
        "glucose",
        "meals",
        "medication",
        "exercise",
        "sleep",
        "stress",
        "symptoms",
        "vitals",
    ):
        assert len(body[key]) == 30, key


async def test_trends_glucose_computes_avg_min_max_count_per_day(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-glucose-math@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, _today_at(8), value=90)
    await _create_glucose(client, token, _today_at(14), value=150)
    await _create_glucose(client, token, _today_at(20), value=120)

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["glucose"][-1]
    assert today_point["count"] == 3
    assert today_point["minimum"] == 90
    assert today_point["maximum"] == 150
    assert today_point["average"] == pytest.approx((90 + 150 + 120) / 3, abs=0.1)


async def test_trends_glucose_normalizes_mixed_units(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-glucose-units@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, _today_at(8), value=100, unit="mg_dl")
    await _create_glucose(client, token, _today_at(20), value=10, unit="mmol_l")

    response_mg_dl = await client.get(
        "/api/patients/me/analytics/trends",
        params={"period": "week", "glucose_unit": "mg_dl"},
        headers=auth_headers(token),
    )
    response_mmol_l = await client.get(
        "/api/patients/me/analytics/trends",
        params={"period": "week", "glucose_unit": "mmol_l"},
        headers=auth_headers(token),
    )
    mg_dl_point = response_mg_dl.json()["glucose"][-1]
    mmol_l_point = response_mmol_l.json()["glucose"][-1]
    # 10 mmol/L -> ~180.2 mg/dL; average of (100, 180.2) -> ~140.1 mg/dL.
    assert mg_dl_point["average"] == pytest.approx(140.1, abs=0.1)
    assert mmol_l_point["average"] == pytest.approx(140.1 / 18.0182, abs=0.1)


async def test_trends_meal_count_and_average_carbs(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-meals@example.com")
    token = reg["tokens"]["access_token"]

    await _create_meal_with_carbs(client, token, _today_at(8), estimated_carbs_g=40)
    await _create_meal_with_carbs(client, token, _today_at(12), estimated_carbs_g=60)
    await _create_meal_with_carbs(client, token, _today_at(18), estimated_carbs_g=None)

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["meals"][-1]
    assert today_point["count"] == 3
    # Average only over the two meals with a recorded carb estimate.
    assert today_point["average_carbs_g"] == pytest.approx((40 + 60) / 2, abs=0.01)


async def test_trends_medication_adherence_pct(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-medication@example.com")
    token = reg["tokens"]["access_token"]
    medication_id = await _create_medication(client, token)

    await _create_medication_log(client, token, medication_id, _today_at(8), taken=True)
    await _create_medication_log(client, token, medication_id, _today_at(13), taken=True)
    await _create_medication_log(client, token, medication_id, _today_at(18), taken=True)
    await _create_medication_log(client, token, medication_id, _today_at(21), taken=False)

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["medication"][-1]
    assert today_point["taken_count"] == 3
    assert today_point["missed_count"] == 1
    assert today_point["adherence_pct"] == pytest.approx(75.0, abs=0.01)


async def test_trends_exercise_total_minutes_and_session_count(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-exercise@example.com")
    token = reg["tokens"]["access_token"]

    await _create_exercise(client, token, _today_at(7), duration_minutes=20)
    await _create_exercise(client, token, _today_at(18), duration_minutes=40)

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["exercise"][-1]
    assert today_point["total_minutes"] == 60
    assert today_point["session_count"] == 2


async def test_trends_sleep_average_hours_and_quality_score(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-sleep@example.com")
    token = reg["tokens"]["access_token"]

    await _create_sleep_with(client, token, _today_at(7), hours_slept=6.0, quality="fair")
    await _create_sleep_with(client, token, _today_at(8), hours_slept=8.0, quality="good")

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["sleep"][-1]
    assert today_point["average_hours"] == pytest.approx(7.0, abs=0.01)
    # fair=2, good=3 -> average 2.5
    assert today_point["average_quality_score"] == pytest.approx(2.5, abs=0.01)


async def test_trends_stress_averages_and_ignores_missing_energy(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-stress@example.com")
    token = reg["tokens"]["access_token"]

    await _create_stress_with(client, token, _today_at(9), stress_level=4, energy_level=8)
    await _create_stress_with(client, token, _today_at(17), stress_level=6, energy_level=None)

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["stress"][-1]
    assert today_point["average_stress_level"] == pytest.approx(5.0, abs=0.01)
    # Only one of the two entries recorded an energy level.
    assert today_point["average_energy_level"] == pytest.approx(8.0, abs=0.01)


async def test_trends_symptom_count(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-symptom@example.com")
    token = reg["tokens"]["access_token"]

    await _create_symptom(client, token, _today_at(10))
    await _create_symptom(client, token, _today_at(15))

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["symptoms"][-1]
    assert today_point["count"] == 2


async def test_trends_vitals_tracks_latest_non_null_value_per_field(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-vitals@example.com")
    token = reg["tokens"]["access_token"]

    await _create_vitals_with(
        client, token, _today_at(8), weight_kg=70.0, systolic=120, diastolic=80
    )
    # Later entry only updates weight — systolic/diastolic should still
    # reflect the earlier reading, not be wiped to null.
    await _create_vitals_with(
        client, token, _today_at(18), weight_kg=71.0, systolic=None, diastolic=None
    )

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    today_point = response.json()["vitals"][-1]
    assert today_point["latest_weight_kg"] == pytest.approx(71.0, abs=0.01)
    assert today_point["latest_blood_pressure_systolic"] == 120
    assert today_point["latest_blood_pressure_diastolic"] == 80


async def test_trends_excludes_events_outside_period(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-outside@example.com")
    token = reg["tokens"]["access_token"]

    today = datetime.now(UTC).date()
    too_old = datetime(today.year, today.month, today.day, tzinfo=UTC) - timedelta(days=10)
    await _create_glucose(client, token, too_old.isoformat(), value=999)
    await _create_symptom(client, token, too_old.isoformat())

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "week"}, headers=auth_headers(token)
    )
    body = response.json()
    assert all(p["count"] == 0 for p in body["glucose"])
    assert all(p["count"] == 0 for p in body["symptoms"])


async def test_trends_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "trendA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "trendB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    await _create_glucose(client, token_a, _today_at(8), value=200)
    await _create_symptom(client, token_a, _today_at(8))

    response = await client.get(
        "/api/patients/me/analytics/trends",
        params={"period": "week"},
        headers=auth_headers(token_b),
    )
    body = response.json()
    assert all(p["count"] == 0 for p in body["glucose"])
    assert all(p["count"] == 0 for p in body["symptoms"])


async def test_trends_invalid_period_returns_422(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-badperiod@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.get(
        "/api/patients/me/analytics/trends", params={"period": "year"}, headers=auth_headers(token)
    )
    assert response.status_code == 422


async def test_trends_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/patients/me/analytics/trends")
    assert response.status_code == 401
