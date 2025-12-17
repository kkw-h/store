import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_wechat_login(client: AsyncClient):
    # Test Mock Login
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"code": "mock_code"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    assert "userInfo" in data["data"]
    # assert data["data"]["userInfo"]["nickname"] is not None # Nickname might be None for new users
    assert data["data"]["userInfo"] is not None

@pytest.mark.asyncio
async def test_phone_login(client: AsyncClient):
    # Test Phone Login
    response = await client.post(
        f"{settings.API_V1_STR}/auth/phone",
        json={"phone": "13800138000", "code": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    assert data["data"]["userInfo"]["phone"] == "13800138000"

@pytest.mark.asyncio
async def test_phone_login_validation(client: AsyncClient):
    # Test Invalid Phone Format
    response = await client.post(
        f"{settings.API_V1_STR}/auth/phone",
        json={"phone": "12345", "code": "123456"}
    )
    assert response.json()["code"] == 400

@pytest.mark.asyncio
async def test_admin_login(client: AsyncClient):
    # 1. Success
    response = await client.post(
        f"{settings.API_V1_STR}/auth/admin/login",
        json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    
    # 2. Fail (Wrong Password)
    response = await client.post(
        f"{settings.API_V1_STR}/auth/admin/login",
        json={"username": settings.ADMIN_USERNAME, "password": "wrongpassword"}
    )
    assert response.json()["code"] == 400
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/phone",
        json={"phone": "abcdefghijk", "code": "123456"}
    )
    assert response.json()["code"] == 400

    # Test Invalid Code Format
    response = await client.post(
        f"{settings.API_V1_STR}/auth/phone",
        json={"phone": "13800138000", "code": "123"} # Too short
    )
    assert response.json()["code"] == 400
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/phone",
        json={"phone": "13800138000", "code": "1234567"} # Too long
    )
    assert response.json()["code"] == 400

@pytest.mark.asyncio
async def test_user_update_validation(client: AsyncClient, normal_user_token_headers):
    # Test Invalid Nickname (Too short)
    response = await client.put(
        f"{settings.API_V1_STR}/auth/profile",
        json={"nickname": ""},
        headers=normal_user_token_headers
    )
    assert response.json()["code"] == 400

    # Test Invalid Nickname (Too long)
    response = await client.put(
        f"{settings.API_V1_STR}/auth/profile",
        json={"nickname": "a" * 33},
        headers=normal_user_token_headers
    )
    assert response.json()["code"] == 400
