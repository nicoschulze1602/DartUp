import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.throw_service import ThrowService
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.throw import Throw


# ---------------------------------------------------------
# Hilfsobjekte erstellen
# ---------------------------------------------------------
def make_game():
    g = Game()
    g.id = 1
    g.game_mode = MagicMock(
        scoring_type="subtract",
        checkout_rule="double",
        starting_score=501
    )
    return g


def make_participant(score=501, user_id=10):
    p = GameParticipant()
    p.id = 50
    p.user_id = user_id
    p.current_score = score
    p.starting_score = score
    return p


def make_throw(value=20, multiplier=1):
    t = Throw()
    t.value = value
    t.multiplier = multiplier
    return t


# ---------------------------------------------------------
# MAIN TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_throw_service_ok():
    """
    Normaler Wurf → Engine liefert OK → ThrowService soll korrektes Response zurückgeben.
    """
    game = make_game()
    participant = make_participant(501)
    throw = make_throw(20, 1)

    db = AsyncMock()

    # Engine Mock → OK Treffer (501 → 481)
    with patch("app.services.throw_service.GameEngine.apply_throw") as mock_engine:
        mock_engine.return_value = {"status": "OK", "remaining": 481}

        # TurnService Mock
        with patch("app.services.throw_service.TurnService.get_throw_position") as mock_turn:
            mock_turn.return_value = (1, 1)  # turn 1, throw 1

            # CRUD: save_throw → wir simulieren ein ThrowOut ORM Objekt
            with patch("app.services.throw_service.save_throw") as mock_save:
                saved_throw = MagicMock()
                saved_throw.id = 999
                saved_throw.value = 20
                saved_throw.multiplier = 1
                saved_throw.score = 20
                saved_throw.turn_number = 1
                saved_throw.throw_number_in_turn = 1
                mock_save.return_value = saved_throw

                response = await ThrowService.perform_throw(
                    db=db,
                    game=game,
                    participant=participant,
                    throw=throw
                )

    assert response.status == "OK"
    assert response.remaining == 481
    assert response.throw.id == 999
    assert response.throw_in_turn == "1/3"
    assert response.player is not None


@pytest.mark.asyncio
async def test_throw_service_bust():
    game = make_game()
    participant = make_participant(20)
    throw = make_throw(25, 2)  # würde überwerfen

    db = AsyncMock()

    with patch("app.services.throw_service.GameEngine.apply_throw") as mock_engine:
        mock_engine.return_value = {"status": "BUST", "remaining": 20}

        with patch("app.services.throw_service.TurnService.get_throw_position") as mock_turn:
            mock_turn.return_value = (4, 1)  # turn 4, throw 1

            with patch("app.services.throw_service.save_throw") as mock_save:
                saved_throw = MagicMock()
                saved_throw.id = 998
                saved_throw.turn_number = 4
                saved_throw.throw_number_in_turn = 1
                mock_save.return_value = saved_throw

                response = await ThrowService.perform_throw(
                    db=db,
                    game=game,
                    participant=participant,
                    throw=throw
                )

    assert response.status == "BUST"
    assert response.remaining == 20


@pytest.mark.asyncio
async def test_throw_service_win():
    game = make_game()
    participant = make_participant(40)
    throw = make_throw(20, 2)  # double → finish

    db = AsyncMock()

    with patch("app.services.throw_service.GameEngine.apply_throw") as mock_engine:
        mock_engine.return_value = {"status": "WIN", "remaining": 0}

        with patch("app.services.throw_service.TurnService.get_throw_position") as mock_turn:
            mock_turn.return_value = (5, 3)

            with patch("app.services.throw_service.save_throw") as mock_save:
                saved_throw = MagicMock()
                saved_throw.id = 997
                saved_throw.turn_number = 5
                saved_throw.throw_number_in_turn = 3
                mock_save.return_value = saved_throw

                # finish_game Mock
                with patch("app.services.throw_service.finish_game") as mock_finish:
                    mock_finish.return_value = None

                    response = await ThrowService.perform_throw(
                        db=db,
                        game=game,
                        participant=participant,
                        throw=throw
                    )

    assert response.status == "WIN"
    assert response.remaining == 0