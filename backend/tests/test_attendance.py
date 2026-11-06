import random
from datetime import date, timedelta
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_teacher_a_records_attendance_success(client: AsyncClient, teacher_a_token: str, admin_token: str):
    # Get Ravi's student_id and Class 10A class_id
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    cls_res = await client.get("/api/classes", headers={"Authorization": f"Bearer {admin_token}"})
    c10a = next(c for c in cls_res.json()["data"] if c["name"] == "Class 10" and c["section"] == "A")
    class_id = c10a["id"]

    unique_date = str(date.today() + timedelta(days=random.randint(100, 5000)))

    response = await client.post(
        "/api/attendance",
        headers={"Authorization": f"Bearer {teacher_a_token}"},
        json={
            "student_id": ravi_id,
            "class_id": class_id,
            "attendance_date": unique_date,
            "session": "morning",
            "status": "present"
        }
    )
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True

@pytest.mark.asyncio
async def test_duplicate_attendance_rejection(client: AsyncClient, teacher_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    cls_res = await client.get("/api/classes", headers={"Authorization": f"Bearer {admin_token}"})
    c10a = next(c for c in cls_res.json()["data"] if c["name"] == "Class 10" and c["section"] == "A")
    class_id = c10a["id"]

    # Ravi already has attendance recorded for TODAY in seed data with session="full_day"
    response = await client.post(
        "/api/attendance",
        headers={"Authorization": f"Bearer {teacher_a_token}"},
        json={
            "student_id": ravi_id,
            "class_id": class_id,
            "attendance_date": str(date.today()),
            "session": "full_day",
            "status": "present"
        }
    )
    assert response.status_code == 409
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "DUPLICATE_ATTENDANCE"

@pytest.mark.asyncio
async def test_teacher_b_cannot_record_class_10a_attendance(client: AsyncClient, teacher_b_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    cls_res = await client.get("/api/classes", headers={"Authorization": f"Bearer {admin_token}"})
    c10a = next(c for c in cls_res.json()["data"] if c["name"] == "Class 10" and c["section"] == "A")
    class_id = c10a["id"]

    response = await client.post(
        "/api/attendance",
        headers={"Authorization": f"Bearer {teacher_b_token}"},
        json={
            "student_id": ravi_id,
            "class_id": class_id,
            "attendance_date": str(date.today() + timedelta(days=25)),
            "session": "morning",
            "status": "present"
        }
    )
    assert response.status_code == 403
    res = response.json()
    assert res["error"]["code"] == "TEACHER_NOT_ASSIGNED"

@pytest.mark.asyncio
async def test_student_not_in_class_attendance_rejection(client: AsyncClient, teacher_a_token: str, admin_token: str):
    # Priya Mehta is in Class 10B, not Class 10A
    stu_res = await client.get("/api/students?search=Priya", headers={"Authorization": f"Bearer {admin_token}"})
    priya_id = stu_res.json()["data"][0]["id"]

    cls_res = await client.get("/api/classes", headers={"Authorization": f"Bearer {admin_token}"})
    c10a = next(c for c in cls_res.json()["data"] if c["name"] == "Class 10" and c["section"] == "A")
    class_id = c10a["id"]

    response = await client.post(
        "/api/attendance",
        headers={"Authorization": f"Bearer {teacher_a_token}"},
        json={
            "student_id": priya_id,
            "class_id": class_id,
            "attendance_date": str(date.today() + timedelta(days=26)),
            "session": "morning",
            "status": "present"
        }
    )
    assert response.status_code == 400
    res = response.json()
    assert res["error"]["code"] == "STUDENT_NOT_IN_CLASS"

@pytest.mark.asyncio
async def test_admin_can_record_attendance_for_any_class(client: AsyncClient, admin_token: str):
    stu_res = await client.get("/api/students?search=Priya", headers={"Authorization": f"Bearer {admin_token}"})
    priya_id = stu_res.json()["data"][0]["id"]

    cls_res = await client.get("/api/classes", headers={"Authorization": f"Bearer {admin_token}"})
    c10b = next(c for c in cls_res.json()["data"] if c["name"] == "Class 10" and c["section"] == "B")
    class_id = c10b["id"]

    unique_date = str(date.today() + timedelta(days=random.randint(5001, 9999)))

    response = await client.post(
        "/api/attendance",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "student_id": priya_id,
            "class_id": class_id,
            "attendance_date": unique_date,
            "session": "morning",
            "status": "present"
        }
    )
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_attendance_summary_counts(client: AsyncClient, admin_token: str):
    cls_res = await client.get("/api/classes", headers={"Authorization": f"Bearer {admin_token}"})
    c10a = next(c for c in cls_res.json()["data"] if c["name"] == "Class 10" and c["section"] == "A")

    date_from = str(date.today() - timedelta(days=10))
    date_to = str(date.today() + timedelta(days=1))

    response = await client.get(
        f"/api/attendance/class/{c10a['id']}?date_from={date_from}&date_to={date_to}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    summary = res["data"]["summary"]
    assert "present_count" in summary
    assert "absent_count" in summary
    assert summary["present_count"] > 0

@pytest.mark.asyncio
async def test_guardian_can_view_own_student_attendance(client: AsyncClient, guardian_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/attendance/student/{ravi_id}",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_guardian_cannot_view_other_student_attendance(client: AsyncClient, guardian_a_token: str, admin_token: str):
    stu_res = await client.get("/api/students?search=Priya", headers={"Authorization": f"Bearer {admin_token}"})
    priya_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/attendance/student/{priya_id}",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert response.status_code == 403

