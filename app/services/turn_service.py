from app.models.throw import Throw
from app.models.game_participant import GameParticipant

class TurnService:

    @staticmethod
    def get_throw_position(previous_throws: list[Throw]) -> tuple[int, int, int]:
        """
        Berechnet turn_number, throw_number_in_turn und darts_thrown basierend auf den bisherigen Würfen.
        """
        if not previous_throws:
            return 1, 1, 1  # erster Wurf im Spiel

        last_throw = previous_throws[-1]
        darts_thrown = len(previous_throws) + 1
        throws_per_turn = 3

        if last_throw.throw_number_in_turn < throws_per_turn:
            # noch im selben Turn
            return last_throw.turn_number, last_throw.throw_number_in_turn + 1, darts_thrown
        else:
            # next turn
            return last_throw.turn_number + 1, 1, darts_thrown

    @staticmethod
    def get_next_player(game, current_participant: GameParticipant, status: str, throw_number_in_turn: int) -> str:
        """
        Entscheidet, wer als nächstes werfen darf.
        """
        participants = game.participants
        current_index = participants.index(current_participant)

        if status in ["BUST", "WIN"] or throw_number_in_turn == 3:
            # next players turn
            next_index = (current_index + 1) % len(participants)
            return participants[next_index].user.username
        else:
            # same player (next dart)
            return f"{current_participant.user.username} (nächster Dart)"