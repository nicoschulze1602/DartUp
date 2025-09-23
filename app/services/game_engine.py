# app/services/game_engine.py

from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant


class GameEngine:
    """
    Spiellogik für unterschiedliche Dart-Spielmodi.
    """

    @staticmethod
    def apply_throw(game: Game, participant: GameParticipant, throw: Throw):
        """
        Wendet einen Wurf auf das Spiel an – abhängig vom Modus.
        """
        if game.game_mode.name == "501":
            return GameEngine._play_501(participant, throw)
        else:
            raise ValueError(f"Unbekannter Spielmodus: {game.game_mode.name}")

    # ---------- 501 Double Out ----------
    @staticmethod
    def _play_501(participant: GameParticipant, throw: Throw):
        points = throw.value * throw.multiplier
        new_score = participant.current_score - points

        # BUST
        if new_score < 0:
            return {"status": "BUST", "remaining": participant.current_score}

        # Check auf Sieg
        if new_score == 0:
            if throw.multiplier == 2 or (throw.value == 25 and throw.multiplier == 2):
                participant.current_score = 0
                return {"status": "WIN", "remaining": 0}
            else:
                return {"status": "BUST", "remaining": participant.current_score}

        # Normalfall
        participant.current_score = new_score
        return {"status": "OK", "remaining": new_score}