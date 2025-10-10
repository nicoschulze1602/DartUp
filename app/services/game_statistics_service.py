from typing import List, Dict
from app.models.throw import Throw
from app.models.game_participant import GameParticipant


def _mean(values: List[float]) -> float:
    """Einfache lokale mean-Implementierung (vermeidet Konflikte mit einer lokalen statistics.py)."""
    return sum(values) / len(values) if values else 0.0


class GameStatisticsService:
    """
    Berechnet laufende und aggregierte Spielstatistiken
    für Teilnehmer und komplette Spiele.
    """

    # ----------------------------------------------------------
    # 📊 Laufende Spielerstatistiken
    # ----------------------------------------------------------
    @staticmethod
    def calculate_live_stats(_participant: GameParticipant, throws: List[Throw]) -> Dict[str, float | int | None]:
        """
        Berechnet Spielstatistiken für einen einzelnen Teilnehmer.
        Das _participant-Argument ist aktuell ungenutzt, bleibt aber
        für spätere Erweiterungen (z. B. Leg-Auswertung) bestehen.
        """
        if not throws:
            return {
                "three_dart_average": 0,
                "first_9_average": 0,
                "highest_score": 0,
                "checkout_percentage": 0,
                "best_leg": None,
            }

        # Alle Scorings pro Turn sammeln
        turns: Dict[int, List[int]] = {}
        for t in throws:
            turn = turns.setdefault(t.turn_number, [])
            turn.append(t.value * t.multiplier)

        # Summen der Turns berechnen
        turn_sums = [sum(v) for v in turns.values()]

        three_dart_avg = _mean(turn_sums)
        first_9_turns = turn_sums[:3]
        first_9_avg = _mean(first_9_turns)

        return {
            "three_dart_average": round(three_dart_avg, 2),
            "first_9_average": round(first_9_avg, 2),
            "highest_score": max(turn_sums, default=0),
            "checkout_percentage": 0,  # TODO: reales Checkout-Tracking implementieren
            "best_leg": None,           # TODO: Leg-Erkennung bei WIN
        }

    # ----------------------------------------------------------
    # 🧩 Gesamtspielstatistik
    # ----------------------------------------------------------
    @staticmethod
    def calculate_game_stats(game) -> Dict[str, float | int]:
        """
        Aggregiert Statistiken für das gesamte Spiel (alle Teilnehmer).
        Gruppiert Würfe pro Turn, um unrealistische Werte zu vermeiden.
        """
        all_turn_sums: List[int] = []

        for p in game.participants:
            turns: Dict[int, List[int]] = {}
            for t in p.throws:
                turn = turns.setdefault(t.turn_number, [])
                turn.append(t.value * t.multiplier)
            all_turn_sums.extend(sum(vals) for vals in turns.values())

        avg_all = _mean(all_turn_sums)

        return {
            "avg_all_throws": round(avg_all, 2),
            "total_throws": len(all_turn_sums),
        }