import uuid

from httpx import AsyncClient


async def register_patient(client: AsyncClient, email: str) -> dict:
    response = await client.post(
        "/api/auth/register", json={"email": email, "password": "supersecret123"}
    )
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_get_profile_initial_state(client: AsyncClient) -> None:
    reg = await register_patient(client, "profile1@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["medical_history"] is None
    assert body["lifestyle_profile"] is None
    assert body["medications"] == []
    assert body["patient"]["bmi"] is None


async def test_profile_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/patients/me/profile")
    assert response.status_code == 401


async def test_update_profile_computes_bmi(client: AsyncClient) -> None:
    reg = await register_patient(client, "profile2@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.put(
        "/api/patients/me/profile",
        json={"height_cm": 180, "weight_kg": 81},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["bmi"] == 25.0


async def test_update_profile_ignores_client_supplied_bmi(client: AsyncClient) -> None:
    reg = await register_patient(client, "profile3@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.put(
        "/api/patients/me/profile",
        json={"height_cm": 180, "weight_kg": 81, "bmi": 999},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["bmi"] == 25.0


async def test_update_profile_partial_update_preserves_other_fields(client: AsyncClient) -> None:
    reg = await register_patient(client, "profile4@example.com")
    token = reg["tokens"]["access_token"]

    await client.put(
        "/api/patients/me/profile",
        json={"age": 45, "occupation": "teacher"},
        headers=auth_headers(token),
    )
    response = await client.put(
        "/api/patients/me/profile",
        json={"occupation": "nurse"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["age"] == 45
    assert body["occupation"] == "nurse"


async def test_upsert_medical_history_create_then_update(client: AsyncClient) -> None:
    reg = await register_patient(client, "mh@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.put(
        "/api/patients/me/medical-history",
        json={"diabetes_type": "type2", "years_since_diagnosis": 3},
        headers=auth_headers(token),
    )
    assert create.status_code == 200
    assert create.json()["diabetes_type"] == "type2"

    update = await client.put(
        "/api/patients/me/medical-history",
        json={"years_since_diagnosis": 4},
        headers=auth_headers(token),
    )
    assert update.status_code == 200
    assert update.json()["years_since_diagnosis"] == 4
    assert update.json()["diabetes_type"] == "type2"

    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    assert profile.json()["medical_history"]["years_since_diagnosis"] == 4


async def test_upsert_lifestyle_profile(client: AsyncClient) -> None:
    reg = await register_patient(client, "lifestyle@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.put(
        "/api/patients/me/lifestyle",
        json={"sleep_hours_avg": 6.5, "stress_level_baseline": 7},
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["stress_level_baseline"] == 7


async def test_lifestyle_stress_level_out_of_range_rejected(client: AsyncClient) -> None:
    reg = await register_patient(client, "lifestyle2@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.put(
        "/api/patients/me/lifestyle",
        json={"stress_level_baseline": 11},
        headers=auth_headers(token),
    )
    assert response.status_code == 422


async def test_medication_crud_and_soft_delete(client: AsyncClient) -> None:
    reg = await register_patient(client, "meds@example.com")
    token = reg["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/medications",
        json={"name": "Metformin", "dosage": "500mg", "frequency": "twice daily"},
        headers=auth_headers(token),
    )
    assert create.status_code == 201
    medication_id = create.json()["id"]
    assert create.json()["is_active"] is True

    listed = await client.get("/api/patients/me/medications", headers=auth_headers(token))
    assert len(listed.json()) == 1

    updated = await client.put(
        f"/api/patients/me/medications/{medication_id}",
        json={"dosage": "1000mg"},
        headers=auth_headers(token),
    )
    assert updated.status_code == 200
    assert updated.json()["dosage"] == "1000mg"

    deleted = await client.delete(
        f"/api/patients/me/medications/{medication_id}", headers=auth_headers(token)
    )
    assert deleted.status_code == 204

    listed_after = await client.get("/api/patients/me/medications", headers=auth_headers(token))
    body = listed_after.json()
    assert len(body) == 1
    assert body[0]["is_active"] is False

    profile = await client.get("/api/patients/me/profile", headers=auth_headers(token))
    assert profile.json()["medications"] == []


async def test_missing_medication_returns_404(client: AsyncClient) -> None:
    reg = await register_patient(client, "notfound@example.com")
    token = reg["tokens"]["access_token"]

    fake_id = uuid.uuid4()
    response = await client.put(
        f"/api/patients/me/medications/{fake_id}",
        json={"dosage": "1000mg"},
        headers=auth_headers(token),
    )
    assert response.status_code == 404

    delete_response = await client.delete(
        f"/api/patients/me/medications/{fake_id}", headers=auth_headers(token)
    )
    assert delete_response.status_code == 404


async def test_baseline_assessment_submission(client: AsyncClient) -> None:
    reg = await register_patient(client, "baseline@example.com")
    token = reg["tokens"]["access_token"]

    response = await client.post(
        "/api/patients/me/baseline-assessment",
        json={"notes": "first pass", "raw_answers": {"q1": "yes", "q2": 42}},
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["completed_at"] is not None
    assert body["raw_answers"] == {"q1": "yes", "q2": 42}

    # Resubmitting upserts rather than creating a second row.
    resubmit = await client.post(
        "/api/patients/me/baseline-assessment",
        json={"notes": "revised", "raw_answers": {"q1": "no"}},
        headers=auth_headers(token),
    )
    assert resubmit.status_code == 201
    assert resubmit.json()["notes"] == "revised"
    assert resubmit.json()["raw_answers"] == {"q1": "no"}


async def test_cross_patient_medication_access_is_isolated(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "ownerA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    patient_b = await register_patient(client, "ownerB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    create = await client.post(
        "/api/patients/me/medications",
        json={"name": "Insulin"},
        headers=auth_headers(token_a),
    )
    assert create.status_code == 201
    medication_id = create.json()["id"]

    steal_update = await client.put(
        f"/api/patients/me/medications/{medication_id}",
        json={"dosage": "999mg"},
        headers=auth_headers(token_b),
    )
    assert steal_update.status_code == 404

    steal_delete = await client.delete(
        f"/api/patients/me/medications/{medication_id}", headers=auth_headers(token_b)
    )
    assert steal_delete.status_code == 404

    b_list = await client.get("/api/patients/me/medications", headers=auth_headers(token_b))
    assert b_list.json() == []

    a_list = await client.get("/api/patients/me/medications", headers=auth_headers(token_a))
    assert len(a_list.json()) == 1
    assert a_list.json()[0]["is_active"] is True


async def test_cross_patient_profile_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "profA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    await client.put("/api/patients/me/profile", json={"age": 40}, headers=auth_headers(token_a))

    patient_b = await register_patient(client, "profB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    response = await client.get("/api/patients/me/profile", headers=auth_headers(token_b))
    assert response.status_code == 200
    assert response.json()["patient"]["age"] is None
    assert response.json()["patient"]["id"] != patient_a["user"]["id"]


async def test_cross_patient_medical_history_isolation(client: AsyncClient) -> None:
    patient_a = await register_patient(client, "mhA@example.com")
    token_a = patient_a["tokens"]["access_token"]
    await client.put(
        "/api/patients/me/medical-history",
        json={"diabetes_type": "type1"},
        headers=auth_headers(token_a),
    )

    patient_b = await register_patient(client, "mhB@example.com")
    token_b = patient_b["tokens"]["access_token"]

    response = await client.get("/api/patients/me/profile", headers=auth_headers(token_b))
    assert response.json()["medical_history"] is None
