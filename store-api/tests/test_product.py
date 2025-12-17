import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_category_and_product_flow(client: AsyncClient, normal_user_token_headers):
    # 1. Create Category
    cat_data = {"name": "Test Category", "sort": 1}
    res = await client.post(f"{settings.API_V1_STR}/category", json=cat_data)
    assert res.status_code == 200
    cat_id = res.json()["data"]["id"]

    # 2. Create Product
    prod_data = {
        "category_id": cat_id,
        "name": "Test Product",
        "thumb_url": "http://img",
        "price": "10.00",
        "original_price": "12.00",
        "stock": 100,
        "description": "Desc"
    }
    res = await client.post(f"{settings.API_V1_STR}/product", json=prod_data)
    assert res.status_code == 200
    prod_id = res.json()["data"]["id"]

    # 3. List Products
    res = await client.get(f"{settings.API_V1_STR}/product/list?category_id={cat_id}")
    data = res.json()["data"]
    assert data["total"] >= 1
    assert data["list"][0]["id"] == prod_id

    # 4. Get Detail
    res = await client.get(f"{settings.API_V1_STR}/product/{prod_id}")
    assert res.json()["data"]["name"] == "Test Product"

    # 5. Update Product
    res = await client.put(f"{settings.API_V1_STR}/product/{prod_id}", json={"name": "Updated Name"})
    assert res.json()["data"]["name"] == "Updated Name"
