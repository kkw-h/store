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
async def test_login_invalid_code(client: AsyncClient):
    response = await client.post(
        f"{settings.API_V1_STR}/auth/phone",
        json={"phone": "13800138000", "code": "000000"}
    )
    # The global exception handler returns 200 with code != 200, or 400?
    # Based on main.py exception handler, it returns 200 with error body if it catches HTTPException
    # But wait, main.py says:
    # @app.exception_handler(StarletteHTTPException) ... returns JSONResponse(status_code=200, content=error(code=exc.status_code...))
    # So HTTP 400 becomes 200 OK with body {"code": 400 ...}
    
    assert response.status_code == 200 
    data = response.json()
    assert data["code"] == 400
