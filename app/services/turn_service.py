from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant


class TurnService:

    @staticmethod
    def get_throw_position(previous_throws: list[Throw]) -> dict:
        if not previous_throws:
            return {
                "turn_number": 1,
                "throw_number": 1,
                "darts_thrown": 1,
            }

        last = previous_throws[-1]
        darts_thrown = len(previous_throws) + 1

        if last.throw_number_in_turn < 3:
            return {
                "turn_number": last.turn_number,
                "throw_number": last.throw_number_in_turn + 1,
                "darts_thrown": darts_thrown
            }

        return {
            "turn_number": last.turn_number + 1,
            "throw_number": 1,
            "darts_thrown": darts_thrown
        }

    @staticmethod
    def should_change_player(status: str, throw_number_in_turn: int) -> bool:
        return status in ("WIN", "BUST") or throw_number_in_turn == 3

    @staticmethod
    def get_next_player(game: Game, current_participant: GameParticipant):
        participants = game.participants
        ids = [p.id for p in participants]

        if current_participant.id not in ids:
            return None

        idx = ids.index(current_participant.id)
        return participants[(idx + 1) % len(participants)]

    @staticmethod
    def handle_player_switch(game: Game, participant: GameParticipant, throw_result: str, throw_number_in_turn: int):
        """
        Entscheidet, ob ein Spielerwechsel stattfinden muss
        und gibt Username des nächsten Spielers zurück.
        """
        if TurnService.should_change_player(throw_result, throw_number_in_turn):
            next_p = TurnService.get_next_player(game, participant)
            if next_p and next_p.user:
                return next_p.user.username
            return None

        return participant.user.username