import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_creates_invoice_success(client: AsyncClient, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    response = await client.post(
        "/api/fees/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "student_id": ravi_id,
            "description": "Library Fee",
            "amount_due": 50000,
            "due_date": "2026-12-15"
        }
    )
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    assert res["data"]["amount_due"] == 50000

@pytest.mark.asyncio
async def test_payment_and_computed_balance_lifecycle(client: AsyncClient, admin_token: str):
    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]

    # 1. Create fresh invoice for 500000 paise (₹5000)
    inv_res = await client.post(
        "/api/fees/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "student_id": ravi_id,
            "description": "Annual Fee Test",
            "amount_due": 500000,
            "due_date": "2026-12-31"
        }
    )
    invoice_id = inv_res.json()["data"]["id"]

    # 2. Check initial balance: no payments -> outstanding=500000, status="unpaid"
    b0 = await client.get(
        f"/api/fees/invoices/{invoice_id}/balance",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert b0.status_code == 200
    res0 = b0.json()["data"]
    assert res0["amount_due"] == 500000
    assert res0["total_paid"] == 0
    assert res0["outstanding"] == 500000
    assert res0["status"] == "unpaid"

    # 3. Record partial payment of 200000 -> outstanding=300000, status="partial"
    ref1 = f"PAY_{uuid.uuid4().hex[:6]}"
    p1 = await client.post(
        f"/api/fees/invoices/{invoice_id}/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paid": 200000, "payment_ref": ref1}
    )
    assert p1.status_code == 201
    res1 = p1.json()["data"]["balance"]
    assert res1["total_paid"] == 200000
    assert res1["outstanding"] == 300000
    assert res1["status"] == "partial"

    # 4. Record remaining 300000 -> outstanding=0, status="paid"
    ref2 = f"PAY_{uuid.uuid4().hex[:6]}"
    p2 = await client.post(
        f"/api/fees/invoices/{invoice_id}/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paid": 300000, "payment_ref": ref2}
    )
    assert p2.status_code == 201
    res2 = p2.json()["data"]["balance"]
    assert res2["total_paid"] == 500000
    assert res2["outstanding"] == 0
    assert res2["status"] == "paid"

    # 5. Duplicate payment_ref -> 409 DUPLICATE_PAYMENT_REF
    p_dup = await client.post(
        f"/api/fees/invoices/{invoice_id}/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paid": 10000, "payment_ref": ref1}
    )
    assert p_dup.status_code == 409
    assert p_dup.json()["error"]["code"] == "DUPLICATE_PAYMENT_REF"

    # 6. amount_paid = 0 -> 400 INVALID_PAYMENT_AMOUNT
    p_zero = await client.post(
        f"/api/fees/invoices/{invoice_id}/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paid": 0, "payment_ref": f"PAY_{uuid.uuid4().hex[:6]}"}
    )
    assert p_zero.status_code == 400
    assert p_zero.json()["error"]["code"] == "INVALID_PAYMENT_AMOUNT"

    # 7. amount_paid negative -> 400 INVALID_PAYMENT_AMOUNT
    p_neg = await client.post(
        f"/api/fees/invoices/{invoice_id}/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount_paid": -500, "payment_ref": f"PAY_{uuid.uuid4().hex[:6]}"}
    )
    assert p_neg.status_code == 400
    assert p_neg.json()["error"]["code"] == "INVALID_PAYMENT_AMOUNT"

@pytest.mark.asyncio
async def test_guardian_invoice_authorization(client: AsyncClient, guardian_a_token: str, guardian_b_token: str, admin_token: str):
    # Guardian A owns Ravi's invoice; Guardian B owns Priya's invoice
    invs_res = await client.get("/api/fees/invoices", headers={"Authorization": f"Bearer {admin_token}"})
    all_invoices = invs_res.json()["data"]

    stu_res = await client.get("/api/students?search=Ravi", headers={"Authorization": f"Bearer {admin_token}"})
    ravi_id = stu_res.json()["data"][0]["id"]
    ravi_inv = next(inv for inv in all_invoices if inv["student_id"] == ravi_id)

    # Guardian A accesses Ravi's invoice -> 200
    res_a = await client.get(
        f"/api/fees/invoices/{ravi_inv['id']}",
        headers={"Authorization": f"Bearer {guardian_a_token}"}
    )
    assert res_a.status_code == 200

    # Guardian B tries to access Ravi's invoice -> 403
    res_b = await client.get(
        f"/api/fees/invoices/{ravi_inv['id']}",
        headers={"Authorization": f"Bearer {guardian_b_token}"}
    )
    assert res_b.status_code == 403

