import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_guardian_me_students(client: AsyncClient, guardian_a_token: str):
    response = await client.get(
        "/api/guardian/me/students",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    student_names = [s["full_name"] for s in res["data"]]
    assert "Ravi Sharma" in student_names
    assert "Arjun Singh" in student_names
    assert "Rahul Das" in student_names
    assert "Priya Mehta" not in student_names
    assert "Sneha Patel" not in student_names

@pytest.mark.asyncio
async def test_guardian_accessing_other_student_rejected(client: AsyncClient, guardian_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Priya", headers={"Authorization": f"Bearer {admin_token}"})
    priya_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/guardian/me/students/{priya_id}/attendance",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 403
    res = response.json()
    assert res["error"]["code"] == "NOT_YOUR_STUDENT"

@pytest.mark.asyncio
async def test_guardian_accessing_own_student_attendance(client: AsyncClient, guardian_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/guardian/me/students/{ravi_id}/attendance",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "records" in res["data"]
    assert "summary" in res["data"]

@pytest.mark.asyncio
async def test_guardian_accessing_own_student_report_card(client: AsyncClient, guardian_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/guardian/me/students/{ravi_id}/report-card",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True

@pytest.mark.asyncio
async def test_guardian_accessing_own_student_fee_summary(client: AsyncClient, guardian_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/guardian/me/students/{ravi_id}/fee-summary",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert isinstance(res["data"], list)
    assert len(res["data"]) > 0
    inv = res["data"][0]
    assert "amount_due" in inv
    assert "total_paid" in inv
    assert "outstanding" in inv

