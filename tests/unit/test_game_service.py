import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.game_service import GameService


# -------------------------------------------------------
# Test: start_game ruft nur create_game auf
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_start_game_calls_create_game(async_session: AsyncSession):

    mock_game = {"id": 1}

    with patch("app.services.game_service.create_game", new=AsyncMock(return_value=mock_game)) as mock_create:

        host = type("User", (), {"id": 10})
        mode = type("GameMode", (), {"id": 3})

        result = await GameService.start_game(
            db=async_session,
            host=host,
            game_mode=mode,
            opponent_ids=[2, 3],
            first_to=501,
            first_shot=1
        )

        mock_create.assert_called_once()
        assert result == mock_game


# -------------------------------------------------------
# Test: load_game – normal OK
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_load_game_success(async_session: AsyncSession):

    fake_game = {"id": 1}
    fake_participant = {"id": 11}

    with patch("app.services.game_service.get_game_full", new=AsyncMock(return_value=fake_game)), \
         patch("app.services.game_service.get_participant_by_game_and_user", new=AsyncMock(return_value=fake_participant)):

        game, participant = await GameService.load_game(async_session, 1, 99)

        assert game == fake_game
        assert participant == fake_participant


# -------------------------------------------------------
# Test: load_game – Game nicht gefunden
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_load_game_not_found(async_session: AsyncSession):

    with patch("app.services.game_service.get_game_full", new=AsyncMock(return_value=None)):

        with pytest.raises(HTTPException) as exc:
            await GameService.load_game(async_session, 1, 99)

        assert exc.value.status_code == 404


# -------------------------------------------------------
# Test: load_game – User ist kein Teilnehmer
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_load_game_forbidden(async_session: AsyncSession):

    with patch("app.services.game_service.get_game_full", new=AsyncMock(return_value={"id": 1})), \
         patch("app.services.game_service.get_participant_by_game_and_user", new=AsyncMock(return_value=None)):

        with pytest.raises(HTTPException) as exc:
            await GameService.load_game(async_session, 1, 99)

        assert exc.value.status_code == 403


# -------------------------------------------------------
# Test: finish_game – OK
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_finish_game_success(async_session: AsyncSession):

    mock_game = {"id": 1}

    with patch("app.services.game_service.finish_game_crud", new=AsyncMock(return_value=mock_game)):
        result = await GameService.finish_game(async_session, 1)

        assert result == mock_game


# -------------------------------------------------------
# Test: finish_game – Game nicht gefunden
# -------------------------------------------------------
@pytest.mark.asyncio
async def test_finish_game_not_found(async_session: AsyncSession):

    with patch("app.services.game_service.finish_game_crud", new=AsyncMock(return_value=None)):

        with pytest.raises(HTTPException) as exc:
            await GameService.finish_game(async_session, 999)

        assert exc.value.status_code == 404