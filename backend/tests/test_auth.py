from datetime import timedelta

from httpx import AsyncClient

from app.core.security import create_token


async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register", json={"email": "sprint1@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "sprint1@example.com"
    assert body["user"]["role"] == "patient"
    assert "password" not in body["user"]
    assert "hashed_password" not in body["user"]
    assert body["tokens"]["access_token"]
    assert body["tokens"]["refresh_token"]


async def test_register_duplicate_email_rejected(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": "supersecret123"}
    first = await client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/auth/register", json=payload)
    assert second.status_code == 400


async def test_login_success(client: AsyncClient) -> None:
    await client.post(
        "/api/auth/register", json={"email": "login@example.com", "password": "supersecret123"}
    )
    response = await client.post(
        "/api/auth/login", json={"email": "login@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]


async def test_login_failure_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/auth/register", json={"email": "wrongpw@example.com", "password": "supersecret123"}
    )
    response = await client.post(
        "/api/auth/login", json={"email": "wrongpw@example.com", "password": "not-the-password"}
    )
    assert response.status_code == 401


async def test_login_failure_unknown_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": "supersecret123"}
    )
    assert response.status_code == 401


async def test_me_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


async def test_me_with_valid_token(client: AsyncClient) -> None:
    register = await client.post(
        "/api/auth/register", json={"email": "me@example.com", "password": "supersecret123"}
    )
    access_token = register.json()["tokens"]["access_token"]

    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


async def test_me_with_expired_token_rejected(client: AsyncClient) -> None:
    register = await client.post(
        "/api/auth/register", json={"email": "expired@example.com", "password": "supersecret123"}
    )
    user_id = register.json()["user"]["id"]
    expired_token = create_token(user_id, "access", timedelta(minutes=-1))

    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401


async def test_refresh_returns_new_access_token(client: AsyncClient) -> None:
    register = await client.post(
        "/api/auth/register", json={"email": "refresh@example.com", "password": "supersecret123"}
    )
    refresh_token = register.json()["tokens"]["refresh_token"]

    response = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_refresh_rejects_access_token(client: AsyncClient) -> None:
    register = await client.post(
        "/api/auth/register", json={"email": "refresh2@example.com", "password": "supersecret123"}
    )
    access_token = register.json()["tokens"]["access_token"]

    response = await client.post("/api/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401
