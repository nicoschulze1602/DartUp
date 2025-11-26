import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_register_and_login(async_session: AsyncSession):
    """
    Testet Registrierung + Login mit neuem User.
    """

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        # 1. User registrieren
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "12345"
        }
        r = await client.post("/users/register", json=register_data)
        assert r.status_code == 200
        user = r.json()
        assert user["username"] == "testuser"
        assert "id" in user

        # 2. Login
        login_data = {
            "username": "testuser",
            "password": "12345"
        }
        r = await client.post("/users/login", json=login_data)
        assert r.status_code == 200

        token = r.json()
        assert "access_token" in token
        assert token["token_type"] == "bearer"