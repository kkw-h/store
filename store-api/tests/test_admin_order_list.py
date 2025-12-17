import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_admin_order_list(client: AsyncClient, admin_token_headers):
    # 1. Get List
    res = await client.get(f"{settings.API_V1_STR}/admin/order/list", headers=admin_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    
    # Check structure
    assert "list" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    
    # Check list type
    assert isinstance(data["list"], list)
    if len(data["list"]) > 0:
        first_order = data["list"][0]
        assert "user" in first_order
        # user might be None if user deleted? No, foreign key constraint.
        # But for test created order, we used Admin token?
        # Let's check if user dict is present
        if first_order.get("user"):
            assert "nickname" in first_order["user"]
            assert "phone" in first_order["user"]

