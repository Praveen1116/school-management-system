import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_create_student_success(client: AsyncClient, admin_token: str, guardian_a_token: str):
    # Get guardian id
    me_res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {guardian_a_token}"})
    guardian_id = me_res.json()["data"]["id"]

    new_roll = f"TEST_{uuid.uuid4().hex[:6]}"
    response = await client.post(
        "/api/students",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "guardian_id": guardian_id,
            "full_name": "Test Student",
            "roll_number": new_roll,
            "date_of_birth": "2010-05-15"
        }
    )
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    assert res["data"]["roll_number"] == new_roll

@pytest.mark.asyncio
async def test_duplicate_roll_number(client: AsyncClient, admin_token: str, guardian_a_token: str):
    me_res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {guardian_a_token}"})
    guardian_id = me_res.json()["data"]["id"]

    # STU001 is seeded
    response = await client.post(
        "/api/students",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "guardian_id": guardian_id,
            "full_name": "Duplicate Student",
            "roll_number": "STU001",
            "date_of_birth": "2010-01-01"
        }
    )
    assert response.status_code == 409
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "ROLL_NUMBER_EXISTS"

@pytest.mark.asyncio
async def test_teacher_cannot_create_student(client: AsyncClient, teacher_a_token: str, guardian_a_token: str):
    me_res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {guardian_a_token}"})
    guardian_id = me_res.json()["data"]["id"]

    response = await client.post(
        "/api/students",
        headers={"Authorization": f"Bearer {teacher_a_token}"},
        json={
            "guardian_id": guardian_id,
            "full_name": "Illegal Student",
            "roll_number": f"ILLEGAL_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "2010-01-01"
        }
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_guardian_cannot_create_student(client: AsyncClient, guardian_a_token: str):
    response = await client.post(
        "/api/students",
        headers={"Authorization": f"Bearer {guardian_a_token}"},
        json={
            "guardian_id": str(uuid.uuid4()),
            "full_name": "Illegal Student",
            "roll_number": f"ILLEGAL_{uuid.uuid4().hex[:4]}",
            "date_of_birth": "2010-01-01"
        }
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_list_students_with_pagination(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/students?page=1&limit=2",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]) <= 2
    assert "pagination" in res
    assert res["pagination"]["page"] == 1
    assert res["pagination"]["limit"] == 2

@pytest.mark.asyncio
async def test_search_student_by_name(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/students?search=Ravi",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    names = [s["full_name"] for s in res["data"]]
    assert any("Ravi" in name for name in names)

@pytest.mark.asyncio
async def test_guardian_cannot_list_all_students(client: AsyncClient, guardian_a_token: str):
    response = await client.get(
        "/api/students",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 403

