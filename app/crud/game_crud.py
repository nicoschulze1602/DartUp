from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, UTC

from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.game_mode import GameMode
from app.schemas.game_schemas import GameCreate


async def create_game(db: AsyncSession, game_data: GameCreate, current_user) -> Game:
    """
    Neues Spiel in der DB anlegen.
    Starter ist der eingeloggte User (current_user).
    Gegner kommt aus game_data.opponent_id.
    Beide werden automatisch als GameParticipants eingetragen.
    """
    # Gewählten GameMode laden
    result = await db.execute(select(GameMode).where(GameMode.id == game_data.game_mode_id))
    mode = result.scalars().first()
    if not mode:
        raise ValueError("Invalid game_mode_id")

    # Neues Spiel anlegen (Starter ist current_user)
    new_game = Game(
        user_id=current_user.id,
        game_mode_id=game_data.game_mode_id
    )
    db.add(new_game)
    await db.flush()  # sorgt dafür, dass new_game.id verfügbar ist

    # Startscore aus dem Modus übernehmen
    starter_score = mode.starting_score if mode.starting_score is not None else 0

    # Starter hinzufügen
    starter_participant = GameParticipant(
        game_id=new_game.id,
        user_id=current_user.id,
        starting_score=starter_score,
        current_score=starter_score
    )
    db.add(starter_participant)

    # Gegner hinzufügen
    opponent_participant = GameParticipant(
        game_id=new_game.id,
        user_id=game_data.opponent_id,
        starting_score=starter_score,
        current_score=starter_score
    )
    db.add(opponent_participant)

    # Alles speichern
    await db.commit()
    await db.refresh(new_game)
    return new_game


async def get_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    """
    Hole ein einzelnes Spiel per ID (inkl. Teilnehmer + Würfe).
    """
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.participants), selectinload(Game.throws))
        .where(Game.id == game_id)
    )
    return result.scalars().first()


async def get_games_by_user(db: AsyncSession, user_id: int) -> List[Game]:
    """
    Hole alle Spiele eines bestimmten Users (als Starter).
    """
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.participants))
        .where(Game.user_id == user_id)
    )
    return result.scalars().all()


async def finish_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    """
    Beende ein Spiel (setzt end_time + Status).
    """
    game = await get_game(db, game_id)
    if not game:
        return None

    game.end_time = datetime.now(UTC)
    game.status = "finished"

    await db.commit()
    await db.refresh(game)
    return game