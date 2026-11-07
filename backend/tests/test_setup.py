import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_setup_status_and_lock_when_users_exist(client: AsyncClient):
    """When users exist in the system, setup status is not required and setup POST returns 403."""
    status_res = await client.get("/api/setup/status")
    assert status_res.status_code == 200
    data = status_res.json()["data"]
    assert data["is_setup_required"] is False

    # Attempting to post to setup must return 403 Forbidden permanently
    setup_res = await client.post(
        "/api/setup",
        json={
            "school_name": "Test Academy",
            "school_code": "TA01",
            "full_name": "Principal Skinner",
            "email": "skinner@test.academy",
            "password": "Password@123"
        }
    )
    assert setup_res.status_code == 403
    assert setup_res.json()["error"]["code"] == "SETUP_ALREADY_COMPLETED"
