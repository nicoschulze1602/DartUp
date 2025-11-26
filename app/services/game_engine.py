from app.models.game_participant import GameParticipant
from app.models.throw import Throw
from app.models.game import Game


class GameEngine:
    """
    Pure Spiellogik — verarbeitet einen Wurf basierend auf dem GameMode.
    Führt KEINE DB-Aktionen aus.
    """

    @staticmethod
    def apply_throw(game: Game, participant: GameParticipant, throw: Throw) -> dict:
        """
        Entscheidet, welche Spiellogik angewendet wird.
        Gibt zurück:
        {
            "status": "OK" | "BUST" | "WIN",
            "remaining": <punkte>
        }
        """

        mode = game.game_mode  # enthält: starting_score, scoring_type, checkout_rule, name

        # Dynamisch entscheiden
        if mode.scoring_type == "subtract":
            return GameEngine._play_subtract_mode(participant, throw, mode)

        elif mode.scoring_type == "add":
            return GameEngine._play_add_mode(participant, throw, mode)

        else:
            raise ValueError(f"Unsupported scoring_type: {mode.scoring_type}")

    # -------------------------------------------------------------------------
    # 1️⃣ Klassische X01-Modi (subtract)
    # -------------------------------------------------------------------------
    @staticmethod
    def _play_subtract_mode(participant: GameParticipant, throw: Throw, mode) -> dict:
        """
        Standard X01 Regelwerk: subtract scoring + optional checkout rules.
        """
        points = throw.value * throw.multiplier
        new_score = participant.current_score - points

        # ❌ Überworfen
        if new_score < 0:
            return {"status": "BUST", "remaining": participant.current_score}

        # ❌ 1 Punkt = nicht auscheckbar → Bust (nur bei Double-Out)
        if new_score == 1 and mode.checkout_rule == "double":
            return {"status": "BUST", "remaining": participant.current_score}

        # 🎯 Sieg?
        if new_score == 0:
            if GameEngine._is_valid_checkout(throw, mode):
                participant.current_score = 0
                return {"status": "WIN", "remaining": 0}
            else:
                return {"status": "BUST", "remaining": participant.current_score}

        # ✔ Normaler Treffer
        participant.current_score = new_score
        return {"status": "OK", "remaining": new_score}

    # -------------------------------------------------------------------------
    # 2️⃣ Add-Modi (Cricket, Shanghai etc.)
    # -------------------------------------------------------------------------
    @staticmethod
    def _play_add_mode(participant: GameParticipant, throw: Throw, mode) -> dict:
        """
        Beispielhafte add-Logic (kann später erweitert werden).
        """
        points = throw.value * throw.multiplier
        participant.current_score += points

        # Keine Busts, keine Checkout-Regeln
        return {
            "status": "OK",
            "remaining": participant.current_score
        }

    # -------------------------------------------------------------------------
    # 3️⃣ Checkout-Regel prüfen
    # -------------------------------------------------------------------------
    @staticmethod
    def _is_valid_checkout(throw: Throw, mode) -> bool:
        """
        Prüft, ob der Wurf ein gültiges Checkout ist.
        mode.checkout_rule: "double", "straight", None
        """

        if mode.checkout_rule == "double":
            return throw.multiplier == 2 or (throw.value == 25 and throw.multiplier == 2)

        if mode.checkout_rule == "straight":
            return True

        # Keine Checkout-Regel → alles erlaubt
        return True