import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    # 1. Registrierung
    r = await client.post("/users/register", json={
        "username": "Test User",
        "email": "test@example.com",
        "password": "12345"
    })

    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "Test User"

    # 2. Login
    r = await client.post("/users/login", json={
        "username": "Test User",
        "password": "12345"
    })

    assert r.status_code == 200
    token = r.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"