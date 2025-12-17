import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import sys
import os

# Add project root to sys.path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.core.config import settings
from app.core.database import Base
from app.api import deps

# Use the same database for simplicity in this environment, 
# or use a separate test DB URL if available.
# Ideally: TEST_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/test_db"
TEST_DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest_asyncio.fixture(scope="session")
async def prepare_db():
    # Setup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown: drop tables (Optional, maybe we want to keep data for inspection)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override the dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[deps.get_db] = override_get_db
    
    # Newer httpx versions use transport=ASGITransport(app=app) instead of app=app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def normal_user_token_headers(client: AsyncClient) -> Dict[str, str]:
    # Login to get token
    login_data = {"code": "mock_code"} # Assuming mock logic is enabled
    response = await client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def admin_token_headers(client: AsyncClient) -> Dict[str, str]:
    # For now, admin shares the same login or we assume the first user is admin?
    # The current code doesn't strictly enforce admin roles for the admin endpoints via a role check in DB yet,
    # but the comment says "TODO: Add admin permission check".
    # So we can use the same token for now, or mock a superuser if we implemented that.
    login_data = {"code": "mock_code_admin"} 
    response = await client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}
