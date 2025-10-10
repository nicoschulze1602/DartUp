from app.models.throw import Throw


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
            # nächster Turn
            return last_throw.turn_number + 1, 1, darts_thrown

    @staticmethod
    def get_next_player(game, current_participant, status: str, throw_number_in_turn: int) -> str:
        """
        Entscheidet, wer als Nächstes werfen darf.
        Erwartet ORM-Objekte (Game und GameParticipant), kein JSON.
        """
        participants = game.participants
        if not participants:
            return "Unbekannter Spieler"

        # aktuellen Index im Spiel finden
        current_index = next(
            (i for i, p in enumerate(participants) if p.id == current_participant.id),
            None
        )

        if current_index is None:
            return "Unbekannter Spieler"

        # Wenn Wurfserie vorbei oder Runde gewonnen/gebust → nächster Spieler
        if status in ["BUST", "WIN"] or throw_number_in_turn == 3:
            next_index = (current_index + 1) % len(participants)
            return participants[next_index].user.username

        # sonst bleibt der gleiche Spieler dran
        return f"{current_participant.user.username} (nächster Dart)"