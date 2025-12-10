import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game_mode import GameMode
from app.crud.user_crud import create_user
from app.crud.game_mode_crud import create_game_mode
from app.schemas.game_mode_schemas import GameModeCreate
from app.services.game_service import GameService
from app.schemas.game_schemas import GameCreate


@pytest.mark.asyncio
async def test_throw_route_simple_flow(async_session: AsyncSession, client: AsyncClient):
    """
    Testet die Throw-Route end-to-end:
    - User + GameMode anlegen
    - Game starten
    - 1 Wurf absetzen
    - API-Response prüfen
    """

    # ------------------------------------------------------------
    # 1) Test-Daten vorbereiten
    # ------------------------------------------------------------
    # User erstellen
    user = await create_user(
        async_session,
        username="tester",
        email="tester@example.com",
        password_hash="hashed_pw"
    )

    # GameMode erstellen
    mode = await create_game_mode(
        async_session,
        GameModeCreate(
            name="501 Double Out",
            description="test mode",
            starting_score=501,
            scoring_type="subtract",
            checkout_rule="double"
        )
    )

    # ------------------------------------------------------------
    # 2) Spiel starten (direkt über GameService)
    # ------------------------------------------------------------
    game = await GameService.start_game(
        db=async_session,
        host=user,
        game_mode=mode,
        opponent_ids=[],
        first_to=None,
        first_shot=user.id
    )

    # ------------------------------------------------------------
    # 3) ersten Wurf über die API machen
    # ------------------------------------------------------------
    payload = {
        "value": 20,
        "multiplier": 1,
        "game_id": game.id,
        "participant_id": game.participants[0].id,
    }

    response = await client.post("/throws/", json=payload)
    assert response.status_code == 200, response.text

    data = response.json()

    # ------------------------------------------------------------
    # 4) API-Response prüfen
    # ------------------------------------------------------------
    assert data["throw"]["value"] == 20
    assert data["throw"]["multiplier"] == 1
    assert data["status"] in ("OK", "WIN", "BUST")
    assert "remaining" in data
    assert "next" in data


@pytest.mark.asyncio
async def test_throw_route_invalid_input(async_session: AsyncSession, client: AsyncClient):
    """
    Ungültiger Wurf → 400 BAD REQUEST.
    """
    response = await client.post("/throws/", json={
        "value": 50,   # ungültig
        "multiplier": 1,
        "game_id": 1,
        "participant_id": 1,
    })

    assert response.status_code == 400