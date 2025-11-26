from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.statistic import Statistic
from app.models.game_participant import GameParticipant
from app.models.throw import Throw
from app.models.user import User


class StatisticsService:
    """
    Verwaltet Benutzerstatistiken basierend auf Spiel- und Wurfdaten.
    """
    # ----------------------------------------------------------
    # 🧾 Statistik-Objekt abrufen oder erstellen
    # ----------------------------------------------------------
    @staticmethod
    async def get_or_create_stats(db: AsyncSession, user_id: int) -> Statistic:
        """
        Holt die Statistik eines Users oder legt sie neu an, falls nicht vorhanden.
        """
        result = await db.execute(select(Statistic).where(Statistic.user_id == user_id))
        stats: Statistic | None = result.scalars().first()

        if not stats:
            stats = Statistic(user_id=user_id)
            db.add(stats)
            await db.commit()
            await db.refresh(stats)

        return stats

    # ----------------------------------------------------------
    # 🎯 Nach einem Wurf aktualisieren
    # ----------------------------------------------------------
    @staticmethod
    async def update_after_throw(
        db: AsyncSession,
        participant: GameParticipant,
        throw: Throw,
        result: dict
    ) -> None:
        """
        Aktualisiert die Wurf-bezogene Statistik eines Users.
        """
        user = participant.user
        stats = user.statistics

        stats.total_throws += 1
        score = throw.value * throw.multiplier

        # Durchschnitt neu berechnen
        total_points = stats.average_score_per_turn * (stats.total_throws - 1)
        new_average = (total_points + score) / stats.total_throws
        stats.average_score_per_turn = round(new_average, 2)

        # High Scores (100+, 140+, 180)
        if score >= 100:
            stats.highest_score_per_turn = max(stats.highest_score_per_turn, score)
            if score >= 180:
                stats.total_180s += 1

        await db.commit()
        await db.refresh(user)

    # ----------------------------------------------------------
    # 🏁 Nach Spielende aktualisieren
    # ----------------------------------------------------------
    @staticmethod
    async def update_after_game(
        db: AsyncSession,
        user: User,
        participants: list,
        winner_id: int
    ) -> None:
        """
        Nach Spielende Gesamtstatistik aktualisieren (Win/Loss-Zähler).
        """
        stats = user.statistics
        stats.games_played += 1
        if user.id == winner_id:
            stats.wins += 1
        else:
            stats.losses += 1

        await db.commit()
        await db.refresh(user)