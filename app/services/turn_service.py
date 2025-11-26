# app/services/turn_service.py

from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant


class TurnService:

    # -------------------------------------------------------------------------
    # 1️⃣ TURN- / WURF-POSITION
    # -------------------------------------------------------------------------
    @staticmethod
    def get_throw_position(previous_throws: list[Throw]) -> tuple[int, int, int]:
        """
        Berechnet Turn-Nummer, Wurf-Nr. und Gesamtzahl der Darts.
        """

        if not previous_throws:
            return 1, 1, 1  # erster Wurf im Spiel

        last_throw = previous_throws[-1]

        darts_thrown = len(previous_throws) + 1
        throws_per_turn = 3

        # gleicher Turn
        if last_throw.throw_number_in_turn < throws_per_turn:
            return (
                last_throw.turn_number,
                last_throw.throw_number_in_turn + 1,
                darts_thrown
            )

        # neuer Turn
        return (
            last_throw.turn_number + 1,
            1,
            darts_thrown
        )


    # -------------------------------------------------------------------------
    # 2️⃣ SOLL DER SPIELER WECHSELN?
    # -------------------------------------------------------------------------
    @staticmethod
    def should_change_player(status: str, throw_number_in_turn: int) -> bool:
        """
        Entscheidet, ob ein Spielerwechsel stattfinden muss.
        Regeln:
        - WIN → sofort wechseln
        - BUST → sofort wechseln
        - Nach 3 Darts → wechseln
        """
        if status in ("WIN", "BUST"):
            return True

        if throw_number_in_turn == 3:
            return True

        return False


    # -------------------------------------------------------------------------
    # 3️⃣ NÄCHSTEN SPIELER BESTIMMEN
    # -------------------------------------------------------------------------
    @staticmethod
    def get_next_player(game: Game, current_participant: GameParticipant) -> GameParticipant:
        """
        Gibt den nächsten GameParticipant in der Reihenfolge zurück.
        Kein Username, kein DB – reines Game/Participant-Objekt.
        """

        participants = game.participants

        current_index = next(
            (i for i, p in enumerate(participants) if p.id == current_participant.id),
            None
        )

        if current_index is None:
            return None

        next_index = (current_index + 1) % len(participants)

        return participants[next_index]