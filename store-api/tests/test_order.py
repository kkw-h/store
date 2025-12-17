import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_order_flow(client: AsyncClient, normal_user_token_headers):
    # Setup: Ensure Category and Product exist
    # (In a real test suite, we might use fixtures for these, but chaining is fine for flow test)
    cat_res = await client.post(f"{settings.API_V1_STR}/category", json={"name": "Order Cat"})
    cat_id = cat_res.json()["data"]["id"]
    
    prod_res = await client.post(f"{settings.API_V1_STR}/product", json={
        "category_id": cat_id,
        "name": "Order Product",
        "price": "20.00",
        "stock": 50
    })
    prod_id = prod_res.json()["data"]["id"]

    # Setup: Address
    addr_res = await client.post(f"{settings.API_V1_STR}/address", json={
        "contact_name": "Order User",
        "contact_phone": "13900000009",
        "detail_address": "Order Addr",
        "is_default": True
    }, headers=normal_user_token_headers)
    addr_id = addr_res.json()["data"]["id"]

    # 1. Preview Order
    preview_data = {
        "items": [{"product_id": prod_id, "count": 2}],
        "delivery_type": "delivery"
    }
    res = await client.post(
        f"{settings.API_V1_STR}/order/preview",
        json=preview_data,
        headers=normal_user_token_headers
    )
    assert res.status_code == 200
    p_data = res.json()["data"]
    # 20 * 2 = 40. > 30 so free delivery
    assert float(p_data["total_goods_price"]) == 40.0
    assert float(p_data["delivery_fee"]) == 0.0

    # 2. Create Order (Delivery)
    create_data = {
        "items": [{"product_id": prod_id, "count": 1}],
        "delivery_type": "delivery",
        "address_id": addr_id,
        "remark": "Please hurry"
    }
    res = await client.post(
        f"{settings.API_V1_STR}/order/create",
        json=create_data,
        headers=normal_user_token_headers
    )
    assert res.status_code == 200
    order_id = res.json()["data"]["order_id"]

    # 3. List Orders
    res = await client.get(
        f"{settings.API_V1_STR}/order/list",
        headers=normal_user_token_headers
    )
    list_data = res.json()["data"]
    assert any(o["id"] == order_id for o in list_data)

    # 4. Order Detail
    res = await client.get(
        f"{settings.API_V1_STR}/order/detail?order_id={order_id}",
        headers=normal_user_token_headers
    )
    detail = res.json()["data"]
    assert detail["id"] == order_id
    assert detail["status"] == 1 # Pending Delivery (skipped payment)
    assert len(detail["timeline"]) >= 1

@pytest.mark.asyncio
async def test_admin_flow(client: AsyncClient, admin_token_headers):
    # We need an order first. Let's create one quickly.
    # Note: admin_token_headers is same as user for now due to mock implementation
    
    # Setup Product
    cat_res = await client.post(f"{settings.API_V1_STR}/category", json={"name": "Admin Cat"})
    cat_id = cat_res.json()["data"]["id"]
    prod_res = await client.post(f"{settings.API_V1_STR}/product", json={
        "category_id": cat_id, "name": "Admin Product", "price": "10.00", "stock": 10
    })
    prod_id = prod_res.json()["data"]["id"]
    
    # Create Delivery Order
    addr_res = await client.post(f"{settings.API_V1_STR}/address", json={
        "contact_name": "Admin User", "contact_phone": "139123", "detail_address": "Addr"
    }, headers=admin_token_headers)
    addr_id = addr_res.json()["data"]["id"]
    
    order_res = await client.post(f"{settings.API_V1_STR}/order/create", json={
        "items": [{"product_id": prod_id, "count": 1}],
        "delivery_type": "delivery",
        "address_id": addr_id
    }, headers=admin_token_headers)
    order_id = order_res.json()["data"]["order_id"]
    
    # 1. Audit Accept
    res = await client.post(f"{settings.API_V1_STR}/admin/order/audit", json={
        "order_id": order_id, "action": "accept"
    }, headers=admin_token_headers)
    assert res.json()["code"] == 200
    
    # 2. Complete
    res = await client.post(f"{settings.API_V1_STR}/admin/order/complete_delivery", json={
        "order_id": order_id
    }, headers=admin_token_headers)
    assert res.json()["code"] == 200
    
    # 3. Shop Config
    res = await client.post(f"{settings.API_V1_STR}/admin/shop/config", json={
        "is_open": 1, "open_time": "09:00", "close_time": "21:00"
    }, headers=admin_token_headers)
    assert res.json()["code"] == 200

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
        "user_phone": "138000"
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
