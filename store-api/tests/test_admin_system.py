import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_shop_config(client: AsyncClient, admin_token_headers):
    # 1. Update Config
    payload = {
        "store_name": "My Super Store",
        "is_open": 1,
        "open_time": "08:30",
        "close_time": "22:30",
        "delivery_fee": 5.5,
        "min_order_amount": 30.0,
        "store_address": "Test Address",
        "store_phone": "12345678"
    }
    res = await client.post(f"{settings.API_V1_STR}/admin/shop/config", json=payload, headers=admin_token_headers)
    assert res.status_code == 200
    assert res.json()["code"] == 200

    # 2. Get Config
    res = await client.get(f"{settings.API_V1_STR}/admin/shop/config", headers=admin_token_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["store_name"] == "My Super Store"
    assert data["open_time"] == "08:30"
    assert data["delivery_fee"] == 5.5

@pytest.mark.asyncio
async def test_admin_category_flow(client: AsyncClient, admin_token_headers):
    # 1. Create
    res = await client.post(f"{settings.API_V1_STR}/admin/category/create", json={
        "name": "Admin Cat",
        "sort_order": 10
    }, headers=admin_token_headers)
    assert res.json()["code"] == 200
    
    # 2. List
    res = await client.get(f"{settings.API_V1_STR}/admin/category/list", headers=admin_token_headers)
    data = res.json()["data"]
    assert len(data) > 0
    cat_id = None
    for c in data:
        if c["name"] == "Admin Cat":
            cat_id = c["id"]
            break
    assert cat_id is not None
    
    # 3. Update
    res = await client.post(f"{settings.API_V1_STR}/admin/category/update?id={cat_id}", json={
        "name": "Admin Cat Updated"
    }, headers=admin_token_headers)
    assert res.json()["code"] == 200
    
    # 4. Delete
    # Need to make sure no products attached. Since we just created it, it's empty.
    res = await client.post(f"{settings.API_V1_STR}/admin/category/delete?id={cat_id}", headers=admin_token_headers)
    assert res.json()["code"] == 200

@pytest.mark.asyncio
async def test_admin_product_flow(client: AsyncClient, admin_token_headers):
    # Setup Category
    res = await client.post(f"{settings.API_V1_STR}/admin/category/create", json={"name": "Prod Cat"}, headers=admin_token_headers)
    # Get Cat ID
    res = await client.get(f"{settings.API_V1_STR}/admin/category/list", headers=admin_token_headers)
    cat_id = res.json()["data"][0]["id"]
    
    # 1. Create Product
    prod_payload = {
        "category_id": cat_id,
        "name": "Admin Product",
        "price": 10.0,
        "stock": 100,
        "status": 0 # Off shelf initially
    }
    res = await client.post(f"{settings.API_V1_STR}/admin/product/save", json=prod_payload, headers=admin_token_headers)
    assert res.json()["code"] == 200
    
    # 2. List (Filter)
    res = await client.get(f"{settings.API_V1_STR}/admin/product/list?name=Admin", headers=admin_token_headers)
    data = res.json()["data"]["list"]
    assert len(data) >= 1
    prod_id = data[0]["id"]
    
    # 3. Toggle Status
    res = await client.post(f"{settings.API_V1_STR}/admin/product/status?id={prod_id}&status=1", headers=admin_token_headers)
    assert res.json()["code"] == 200
    
    # 4. Verify Status
    res = await client.get(f"{settings.API_V1_STR}/admin/product/list?status=1", headers=admin_token_headers)
    found = False
    for p in res.json()["data"]["list"]:
        if p["id"] == prod_id:
            found = True
            break
    assert found

    # 5. Delete
    res = await client.post(f"{settings.API_V1_STR}/admin/product/delete?id={prod_id}", headers=admin_token_headers)
    assert res.json()["code"] == 200

@pytest.mark.asyncio
async def test_admin_user_list(client: AsyncClient, admin_token_headers):
    res = await client.get(f"{settings.API_V1_STR}/admin/user/list", headers=admin_token_headers)
    assert res.json()["code"] == 200
    assert "list" in res.json()["data"]
