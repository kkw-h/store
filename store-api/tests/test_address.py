import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_create_and_list_address(client: AsyncClient, normal_user_token_headers):
    # 1. Create Address
    addr_data = {
        "contact_name": "Test User",
        "contact_phone": "13900000001",
        "detail_address": "Test Street 101",
        "is_default": True
    }
    response = await client.post(
        f"{settings.API_V1_STR}/address",
        json=addr_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["contact_name"] == "Test User"
    addr_id = data["data"]["id"]

    # 2. List Addresses
    # Note: The actual endpoint path in app/api/v1/endpoints/address.py is "" for list, not "/list"
    # But wait, let's check app/api/v1/api.py. 
    # It says: api_router.include_router(address.router, prefix="/address", tags=["address"])
    # And in address.py: @router.get("", ...)
    # So the URL is /address, not /address/list
    
    response = await client.get(
        f"{settings.API_V1_STR}/address",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None
    assert len(data["data"]) >= 1
    assert data["data"][0]["id"] == addr_id

@pytest.mark.asyncio
async def test_update_address(client: AsyncClient, normal_user_token_headers):
    # First create one
    addr_data = {
        "contact_name": "Update Me",
        "contact_phone": "13900000002",
        "detail_address": "Original Address",
        "is_default": False
    }
    create_res = await client.post(
        f"{settings.API_V1_STR}/address",
        json=addr_data,
        headers=normal_user_token_headers
    )
    addr_id = create_res.json()["data"]["id"]

    # Update
    update_data = {
        "detail_address": "Updated Address",
        "is_default": True
    }
    response = await client.put(
        f"{settings.API_V1_STR}/address/{addr_id}",
        json=update_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["detail_address"] == "Updated Address"
    assert data["data"]["is_default"] is True

@pytest.mark.asyncio
async def test_delete_address(client: AsyncClient, normal_user_token_headers):
    # Create
    addr_data = {
        "contact_name": "Delete Me",
        "contact_phone": "13900000003",
        "detail_address": "Delete Address",
    }
    create_res = await client.post(
        f"{settings.API_V1_STR}/address",
        json=addr_data,
        headers=normal_user_token_headers
    )
    addr_id = create_res.json()["data"]["id"]

    # Delete
    response = await client.delete(
        f"{settings.API_V1_STR}/address/{addr_id}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_address_validation(client: AsyncClient, normal_user_token_headers):
    # Test Invalid Contact Name (Too short)
    res = await client.post(
        f"{settings.API_V1_STR}/address",
        json={
            "contact_name": "A", 
            "contact_phone": "13900000001",
            "detail_address": "Valid Address"
        },
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400

    # Test Invalid Phone
    res = await client.post(
        f"{settings.API_V1_STR}/address",
        json={
            "contact_name": "Valid Name", 
            "contact_phone": "123", 
            "detail_address": "Valid Address"
        },
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400

    # Test Invalid Detail Address (Too short)
    res = await client.post(
        f"{settings.API_V1_STR}/address",
        json={
            "contact_name": "Valid Name", 
            "contact_phone": "13900000001", 
            "detail_address": "Abc"
        },
        headers=normal_user_token_headers
    )
    assert res.json()["code"] == 400
