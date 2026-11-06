import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_creates_exam_success(client: AsyncClient, admin_token: str):
    sub_res = await client.get("/api/subjects", headers={"Authorization": f"Bearer {admin_token}"})
    math = next(s for s in sub_res.json()["data"] if s["code"] == "MATH")

    response = await client.post(
        "/api/exams",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subject_id": math["id"],
            "grading_rule_set_name": "Standard 2026",
            "name": f"Final Exam {uuid.uuid4().hex[:4]}",
            "total_marks": 100,
            "exam_date": "2026-12-01"
        }
    )
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True

@pytest.mark.asyncio
async def test_enter_result_and_grading_rules(client: AsyncClient, admin_token: str):
    # Get Mathematics subject
    sub_res = await client.get("/api/subjects", headers={"Authorization": f"Bearer {admin_token}"})
    math = next(s for s in sub_res.json()["data"] if s["code"] == "MATH")

    # Create exam
    exam_res = await client.post(
        "/api/exams",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subject_id": math["id"],
            "grading_rule_set_name": "Standard 2026",
            "name": f"Grading Test Exam {uuid.uuid4().hex[:4]}",
            "total_marks": 100,
            "exam_date": "2026-11-15"
        }
    )
    exam_id = exam_res.json()["data"]["id"]

    stu_res = await client.get("/api/students", headers={"Authorization": f"Bearer {admin_token}"})
    students = stu_res.json()["data"]
    s1, s2, s3, s4 = students[0]["id"], students[1]["id"], students[2]["id"], students[3]["id"]

    # 1. marks=92 -> Grade A
    r1 = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": s1, "marks_obtained": 92}
    )
    assert r1.status_code == 201
    assert r1.json()["data"]["grade"] == "A"

    # 2. marks=78 -> Grade B
    r2 = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": s2, "marks_obtained": 78}
    )
    assert r2.status_code == 201
    assert r2.json()["data"]["grade"] == "B"

    # 3. Exact boundary: marks=90 -> Grade A (90-100 inclusive)
    r3 = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": s3, "marks_obtained": 90}
    )
    assert r3.status_code == 201
    assert r3.json()["data"]["grade"] == "A"

    # 4. Exact boundary: marks=89 -> Grade B (75-89 inclusive)
    r4 = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": s4, "marks_obtained": 89}
    )
    assert r4.status_code == 201
    assert r4.json()["data"]["grade"] == "B"

    # 5. marks_obtained > total_marks -> 400 MARKS_EXCEED_TOTAL
    r_exceed = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": str(uuid.uuid4()), "marks_obtained": 105}
    )
    assert r_exceed.status_code == 400
    assert r_exceed.json()["error"]["code"] == "MARKS_EXCEED_TOTAL"

    # 6. marks_obtained < 0 -> 400 INVALID_MARKS
    r_neg = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": str(uuid.uuid4()), "marks_obtained": -5}
    )
    assert r_neg.status_code == 400
    assert r_neg.json()["error"]["code"] == "INVALID_MARKS"

    # 7. Duplicate result (same exam + student) -> 409 RESULT_ALREADY_EXISTS
    r_dup = await client.post(
        f"/api/exams/{exam_id}/results",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"student_id": s1, "marks_obtained": 95}
    )
    assert r_dup.status_code == 409
    assert r_dup.json()["error"]["code"] == "RESULT_ALREADY_EXISTS"

@pytest.mark.asyncio
async def test_teacher_not_assigned_to_subject_rejected(client: AsyncClient, teacher_b_token: str, admin_token: str):
    # Teacher B (Sunita Rao) is assigned to English in 10B, not Mathematics in 10A
    exams_res = await client.get("/api/exams", headers={"Authorization": f"Bearer {admin_token}"})
    exam_math = next(e for e in exams_res.json()["data"] if "Mathematics" in e["name"])

    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.post(
        f"/api/exams/{exam_math['id']}/results",
        headers={"Authorization": f"Bearer {teacher_b_token}"},
        json={"student_id": ravi_id, "marks_obtained": 85}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_student_report_card_aggregation(client: AsyncClient, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.get(
        f"/api/students/{ravi_id}/report-card",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    report_card = res["data"]["report_card"]
    assert isinstance(report_card, list)
    assert len(report_card) > 0
    math_report = next(r for r in report_card if r["subject_code"] == "MATH")
    assert math_report["marks_obtained"] >= 92

