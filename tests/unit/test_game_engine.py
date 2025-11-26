from app.models.game_participant import GameParticipant
from app.models.game import Game
from app.models.game_mode import GameMode
from app.models.throw import Throw


def make_mode(starting_score=501, scoring_type="subtract", checkout_rule="double"):
    return GameMode(
        name="TestMode",
        description="Test",
        starting_score=starting_score,
        scoring_type=scoring_type,
        checkout_rule=checkout_rule,
    )


def make_game(mode: GameMode):
    g = Game(
        id=1,
        user_id=1,
        game_mode_id=1,
        status="ongoing"
    )
    g.game_mode = mode
    return g


def make_participant(score=501):
    return GameParticipant(
        id=1,
        user_id=1,
        game_id=1,
        starting_score=score,
        current_score=score,
    )


def make_throw(value, multiplier):
    return Throw(
        id=1,
        game_id=1,
        participant_id=1,
        value=value,
        multiplier=multiplier,
        score=value * multiplier,
        turn_number=1,
        throw_number_in_turn=1,
    )