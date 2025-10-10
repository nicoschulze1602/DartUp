from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.services.turn_service import TurnService


class GameEngine:
    """
    Spiellogik für verschiedene Dart-Spielmodi.
    """
    @staticmethod
    def apply_throw(game: Game, participant: GameParticipant, throw: Throw):
        """
        Führt einen Dartwurf aus, berechnet neue Punkte und prüft Turnende.
        Enthält einfache print()-Debug-Ausgaben.
        """
        if game.game_mode.name != "501 Double Out":
            raise ValueError(f"Unbekannter Spielmodus: {game.game_mode.name}")

        prev_score = participant.current_score
        result = GameEngine._play_501(participant, throw)
        new_score = participant.current_score

        print(f"🎯 {participant.user.username} wirft {throw.value}x{throw.multiplier} "
              f"= {throw.value * throw.multiplier} Punkte | "
              f"Score: {prev_score} → {new_score} ({result['status']})")

        # ✅ Wenn Turnende → Spielerwechsel
        if result["status"] in ["BUST", "WIN"] or throw.throw_number_in_turn == 3:
            next_player_name = TurnService.get_next_player(
                game, participant, result["status"], throw.throw_number_in_turn
            )
            next_participant = next(
                (p for p in game.participants if p.user.username == next_player_name.split()[0]),
                None
            )
            if next_participant:
                game.current_turn_user_id = next_participant.user_id
                print(f"🔁 Nächster Spieler: {next_participant.user.username}")

        # 🏆 Spiel beenden, falls Sieg
        if result["status"] == "WIN":
            game.status = "finished"
            print(f"🏁 Spiel beendet! Gewinner: {participant.user.username}")

        return result

    # ---------- 501 Double Out ----------
    @staticmethod
    def _play_501(participant: GameParticipant, throw: Throw):
        points = throw.value * throw.multiplier
        new_score = participant.current_score - points

        # ❌ Überworfen
        if new_score < 0:
            print(f"💥 BUST: {participant.user.username} überwirft!")
            return {"status": "BUST", "remaining": participant.current_score}

        # ❌ 1 Punkt = nicht auscheckbar → Bust
        if new_score == 1:
            print(f"🚫 BUST: {participant.user.username} bleibt bei 1 Punkt (nicht auscheckbar).")
            return {"status": "BUST", "remaining": participant.current_score}

        # ✅ Sieg (Double Out)
        if new_score == 0:
            if throw.multiplier == 2 or (throw.value == 25 and throw.multiplier == 2):
                participant.current_score = 0
                print(f"🏆 {participant.user.username} checkt mit Double Out!")
                return {"status": "WIN", "remaining": 0}
            else:
                print(f"😬 Kein Double Out! Bust für {participant.user.username}.")
                return {"status": "BUST", "remaining": participant.current_score}

        # Normaler Treffer
        participant.current_score = new_score
        return {"status": "OK", "remaining": new_score}