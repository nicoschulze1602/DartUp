import pytest
from httpx import AsyncClient
from app.main import app
from sqlalchemy.ext.asyncio import AsyncSession

# ---- Hilfsfunktion ----
@pytest.mark.asyncio
async def test_register_and_login(async_session: AsyncSession):
    """
    Testet Registrierung + Login mit neuem User.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
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

        # 2. Login mit denselben Daten
        login_data = {
            "username": "testuser",
            "password": "12345"
        }
        r = await client.post("/users/login", json=login_data)
        assert r.status_code == 200
        token = r.json()
        assert "access_token" in token
        assert token["token_type"] == "bearer"