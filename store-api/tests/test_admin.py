import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_admin_pickup_flow(client: AsyncClient, admin_token_headers):
    # Setup Product
    cat_res = await client.post(f"{settings.API_V1_STR}/category", json={"name": "Pickup Cat"})
    cat_id = cat_res.json()["data"]["id"]
    prod_res = await client.post(f"{settings.API_V1_STR}/product", json={
        "category_id": cat_id, "name": "Pickup Product", "price": "5.00", "stock": 10
    })
    prod_id = prod_res.json()["data"]["id"]
    
    # Create Pickup Order
    order_res = await client.post(f"{settings.API_V1_STR}/order/create", json={
        "items": [{"product_id": prod_id, "count": 1}],
        "delivery_type": "pickup",
        "pickup_time": "2023-12-30 10:00:00",
        "user_phone": "13800000000"
    }, headers=admin_token_headers)
    order_id = order_res.json()["data"]["order_id"]
    
    # Get Pickup Code from Detail (Assuming admin can see it or user can see it)
    res = await client.get(f"{settings.API_V1_STR}/order/detail?order_id={order_id}", headers=admin_token_headers)
    pickup_code = res.json()["data"]["pickup_code"]
    assert pickup_code is not None
    
    # Verify Pickup
    res = await client.post(f"{settings.API_V1_STR}/admin/order/verify", json={
        "code": pickup_code
    }, headers=admin_token_headers)
    assert res.json()["code"] == 200
    assert res.json()["data"]["success"] is True
    
    # Check Status
    res = await client.get(f"{settings.API_V1_STR}/order/detail?order_id={order_id}", headers=admin_token_headers)
    assert res.json()["data"]["status"] == 4 # Completed

@pytest.mark.asyncio
async def test_admin_validation(client: AsyncClient, admin_token_headers):
    # Test Invalid Shop Config - Time Format
    res = await client.post(f"{settings.API_V1_STR}/admin/shop/config", json={
        "is_open": 1, "open_time": "25:00", "close_time": "21:00",
        "store_name": "Test Shop", "delivery_fee": 0, "min_order_amount": 0
    }, headers=admin_token_headers)
    assert res.json()["code"] == 400

    # Test Invalid Shop Config - is_open
    res = await client.post(f"{settings.API_V1_STR}/admin/shop/config", json={
        "is_open": 2, "open_time": "09:00", "close_time": "21:00",
        "store_name": "Test Shop", "delivery_fee": 0, "min_order_amount": 0
    }, headers=admin_token_headers)
    assert res.json()["code"] == 400

    # Test Invalid Audit Action
    res = await client.post(f"{settings.API_V1_STR}/admin/order/audit", json={
        "order_id": 1, "action": "maybe"
    }, headers=admin_token_headers)
    assert res.json()["code"] == 400
