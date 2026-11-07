import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_can_create_and_list_admin_users(client: AsyncClient, admin_token: str):
    email = f"newadmin_{uuid.uuid4().hex[:6]}@school.demo"
    res = await client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": email,
            "password": "Password123!",
            "role": "admin",
            "full_name": "Vice Principal"
        }
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["email"] == email
    assert data["role"] == "admin"
    assert data["full_name"] == "Vice Principal"

    # List admins specifically
    list_res = await client.get(
        "/api/users?role=admin",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert list_res.status_code == 200
    admin_list = list_res.json()["data"]
    assert any(u["email"] == email for u in admin_list)

@pytest.mark.asyncio
async def test_non_admin_cannot_create_user(client: AsyncClient, teacher_a_token: str):
    res = await client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {teacher_a_token}"},
        json={
            "email": "intruder@school.demo",
            "password": "Password123!",
            "role": "admin"
        }
    )
    assert res.status_code == 403

