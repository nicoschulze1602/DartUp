import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# ---------------------------------------------------------
# 1) Async In-Memory Test-Datenbank
# ---------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with TestSession() as session:
        yield session


# ---------------------------------------------------------
# 2) override get_db für FastAPI → nutzt async_session
# ---------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession):

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()