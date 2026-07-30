from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from tests.test_patients import auth_headers, register_patient
from tests.test_timeline import _create_glucose


def _today_at(hour: int) -> str:
    today = datetime.now(UTC).date()
    return datetime(today.year, today.month, today.day, hour, tzinfo=UTC).isoformat()


async def test_glucose_trend_week_has_seven_points_with_gaps_filled(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-week@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, _today_at(8), value=100)

    response = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "week"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["period"] == "week"
    assert body["unit"] == "mg_dl"
    assert len(body["points"]) == 7

    today = datetime.now(UTC).date()
    assert body["points"][-1]["date"] == today.isoformat()
    assert body["points"][-1]["average"] == 100
    assert body["points"][-1]["count"] == 1
    assert all(p["count"] == 0 and p["average"] is None for p in body["points"][:-1])


async def test_glucose_trend_month_has_thirty_points(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-month@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "month"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert len(response.json()["points"]) == 30


async def test_glucose_trend_computes_avg_min_max_count_per_day(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-math@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, _today_at(8), value=90)
    await _create_glucose(client, token, _today_at(14), value=150)
    await _create_glucose(client, token, _today_at(20), value=120)

    response = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "week"},
        headers=auth_headers(token),
    )
    today_point = response.json()["points"][-1]
    assert today_point["count"] == 3
    assert today_point["minimum"] == 90
    assert today_point["maximum"] == 150
    assert today_point["average"] == pytest.approx((90 + 150 + 120) / 3, abs=0.1)


async def test_glucose_trend_normalizes_mixed_units(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-units@example.com")
    token = reg["tokens"]["access_token"]

    await _create_glucose(client, token, _today_at(8), value=100, unit="mg_dl")
    await _create_glucose(client, token, _today_at(20), value=10, unit="mmol_l")

    response_mg_dl = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "week", "unit": "mg_dl"},
        headers=auth_headers(token),
    )
    response_mmol_l = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "week", "unit": "mmol_l"},
        headers=auth_headers(token),
    )
    mg_dl_point = response_mg_dl.json()["points"][-1]
    mmol_l_point = response_mmol_l.json()["points"][-1]
    # 10 mmol/L -> ~180.2 mg/dL; average of (100, 180.2) -> ~140.1 mg/dL.
    assert mg_dl_point["average"] == pytest.approx(140.1, abs=0.1)
    assert mmol_l_point["average"] == pytest.approx(140.1 / 18.0182, abs=0.1)


async def test_glucose_trend_excludes_readings_outside_period(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-outside@example.com")
    token = reg["tokens"]["access_token"]

    today = datetime.now(UTC).date()
    too_old = datetime(today.year, today.month, today.day, tzinfo=UTC) - timedelta(days=10)
    await _create_glucose(client, token, too_old.isoformat(), value=999)

    response = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "week"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert all(p["count"] == 0 for p in response.json()["points"])


async def test_glucose_trend_cross_patient_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "trendA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "trendB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    await _create_glucose(client, token_a, _today_at(8), value=200)

    response = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "week"},
        headers=auth_headers(token_b),
    )
    assert response.status_code == 200
    assert all(p["count"] == 0 for p in response.json()["points"])


async def test_glucose_trend_invalid_period_returns_422(client: AsyncClient) -> None:
    reg = await register_patient(client, "trend-badperiod@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.get(
        "/api/patients/me/analytics/glucose-trend",
        params={"period": "year"},
        headers=auth_headers(token),
    )
    assert response.status_code == 422


async def test_glucose_trend_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/patients/me/analytics/glucose-trend")
    assert response.status_code == 401
