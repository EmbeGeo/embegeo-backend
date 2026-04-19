import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.database.connection import \
    AsyncSessionLocal as MainAsyncSessionLocal  # Original session local
from app.database.connection import \
    async_engine as main_async_engine  # Original engine
from app.dependencies import get_db
from app.main import app
from app.models.base import Base  # Import Base for metadata

# Override DATABASE_URL for testing — set TEST_DATABASE_URL in .env or environment
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL 환경변수가 설정되지 않았습니다. .env.example을 참고하여 .env에 추가하세요.")

# Create a test engine and session local
test_async_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, pool_size=5, max_overflow=10
)

TestAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Yields the default event loop for the session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """
    Sets up and tears down the test database.
    Creates tables before tests and drops them after tests.
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an independent, clean database session for each test.
    Rolls back transactions after each test.
    """
    connection = await test_async_engine.connect()
    trans = await connection.begin()
    session = TestAsyncSessionLocal(bind=connection)

    # Invalidate the cache to ensure clean state
    # await redis_client.invalidate_latest() # This would require a cache client in fixtures

    yield session

    await trans.rollback()
    await connection.close()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an asynchronous test client for FastAPI.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# You might want to mock Redis if you don't want to run a real Redis for tests
# from unittest.mock import AsyncMock, patch
# @pytest.fixture(autouse=True)
# def mock_redis_client():
#     with patch('app.cache.redis_client.RedisClient', autospec=True) as mock_redis_class:
#         mock_instance = mock_redis_class.return_value
#         mock_instance.connect = AsyncMock(return_value=None)
#         mock_instance.disconnect = AsyncMock(return_value=None)
#         mock_instance.get = AsyncMock(return_value=None)
#         mock_instance.set = AsyncMock(return_value=None)
#         mock_instance.delete = AsyncMock(return_value=None)
#         yield mock_instance
