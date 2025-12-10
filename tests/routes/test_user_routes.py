import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient, async_session: AsyncSession):
    """
    Testet vollständigen Flow:
    1. Registrierung
    2. Login
    """

    # -------------------------------
    # 1️⃣ Registrierung
    # -------------------------------
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


    # -------------------------------
    # 2️⃣ Login
    # -------------------------------
    login_data = {
        "username": "testuser",
        "password": "12345"
    }

    r = await client.post("/users/login", json=login_data)
    assert r.status_code == 200

    token = r.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"