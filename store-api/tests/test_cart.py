import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_cart_lifecycle(client: AsyncClient, normal_user_token_headers):
    # 1. Setup: Create Product
    cat_res = await client.post(f"{settings.API_V1_STR}/category", json={"name": "Cart Cat"})
    cat_id = cat_res.json()["data"]["id"]
    prod_res = await client.post(f"{settings.API_V1_STR}/product", json={
        "category_id": cat_id,
        "name": "Cart Product",
        "price": "100.00",
        "stock": 10
    })
    prod_id = prod_res.json()["data"]["id"]

    # 2. Add to Cart (Valid)
    res = await client.post(
        f"{settings.API_V1_STR}/cart/add",
        json={"product_id": prod_id, "quantity": 1},
        headers=normal_user_token_headers
    )
    assert res.status_code == 200
    assert res.json()["code"] == 200
    
    # 3. Add to Cart (Invalid Quantity - too large)
    res = await client.post(
        f"{settings.API_V1_STR}/cart/add",
        json={"product_id": prod_id, "quantity": 100},
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400
    
    # 4. Add to Cart (Invalid Quantity - zero/negative)
    res = await client.post(
        f"{settings.API_V1_STR}/cart/add",
        json={"product_id": prod_id, "quantity": 0},
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400

    # 5. List Cart
    res = await client.get(
        f"{settings.API_V1_STR}/cart/list",
        headers=normal_user_token_headers
    )
    data = res.json()["data"]
    assert len(data["list"]) >= 1
    cart_item_id = data["list"][0]["id"]

    # 6. Update Cart (Valid)
    res = await client.put(
        f"{settings.API_V1_STR}/cart/update",
        json={"id": cart_item_id, "quantity": 5, "selected": True},
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 200

    # 7. Update Cart (Invalid Quantity)
    res = await client.put(
        f"{settings.API_V1_STR}/cart/update",
        json={"id": cart_item_id, "quantity": 100},
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400

    # 8. Delete Cart
    res = await client.request(
        "DELETE",
        f"{settings.API_V1_STR}/cart/delete",
        json={"ids": [cart_item_id]},
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 200

    # 9. Delete Cart (Empty list)
    res = await client.request(
        "DELETE",
        f"{settings.API_V1_STR}/cart/delete",
        json={"ids": []},
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400
