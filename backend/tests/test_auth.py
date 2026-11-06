import jwt
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient
from config import settings

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@school.demo", "password": "Admin@123"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "access_token" in res["data"]
    assert res["data"]["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@school.demo", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_CREDENTIALS"
    assert res["error"]["message"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_login_non_existent_email(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "nobody@school.demo", "password": "Admin@123"}
    )
    assert response.status_code == 401
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_CREDENTIALS"

@pytest.mark.asyncio
async def test_get_me_valid_token(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["email"] == "admin@school.demo"
    assert res["data"]["role"] == "admin"

@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer this.is.an.invalid.token"}
    )
    assert response.status_code == 401
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_TOKEN"

@pytest.mark.asyncio
async def test_get_me_expired_token(client: AsyncClient):
    expired_payload = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "role": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_TOKEN"

