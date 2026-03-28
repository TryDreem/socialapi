import asyncio
import os
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch, MagicMock

os.environ["ENV_STATE"] = "test"

from app.main import app
from app.database import Base, get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared"




@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop =  asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Creating engine and tables only once for all tests"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        poolclass=StaticPool,
        connect_args={"uri": True},
    )

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()



@pytest_asyncio.fixture
async def db_session(engine):
    connection = await engine.connect()

    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()




@pytest_asyncio.fixture(scope="function")
async def client(db_session):

    if hasattr(app.state, "limiter"):
        app.state.limiter.enabled = False

    """Http client for testing API"""
    async def override_get_db():
        yield db_session
    #pytest will use override_get_db instead of get_db
    app.dependency_overrides[get_db] = override_get_db
    #asgi for httpx to work without starting app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def mock_redis():
    with patch("app.services.post_service.cache_get", return_value=None), \
         patch("app.services.post_service.cache_set", new_callable=AsyncMock), \
         patch("app.services.post_service.cache_pattern_delete", new_callable=AsyncMock), \
         patch("app.api.auth.set_refresh_token", new_callable=AsyncMock), \
         patch("app.api.auth.send_confirmation_email_task") as mock_task:
        mock_task.delay = MagicMock()
        yield



@pytest_asyncio.fixture
async def test_user(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
    }

    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data



@pytest_asyncio.fixture
async def auth_headers(client, test_user, db_session):
    from app.models.user import User
    from sqlalchemy import update

    query = update(User).where(User.email == test_user["email"]).values(is_confirmed=True)
    await db_session.execute(query)
    await db_session.commit()

    response = await client.post("/auth/login", json=test_user)
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_post(client, auth_headers):
    post_data = {
        "body": "test post"
    }

    response = await client.post("/post", json=post_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()