from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.game import Game
from app.schemas.game_schemas import GameCreate
from typing import List, Optional


async def create_game(db: AsyncSession, game_data: GameCreate) -> Game:
    """
    Neues Spiel in der DB anlegen.
    """
    new_game = Game(
        user_id=game_data.user_id,
        mode=game_data.mode
    )
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return new_game


async def get_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    """
    Hole ein einzelnes Spiel per ID.
    """
    result = await db.execute(
        select(Game).where(Game.id == game_id)
    )
    return result.scalars().first()


async def get_games_by_user(db: AsyncSession, user_id: int) -> List[Game]:
    """
    Hole alle Spiele eines bestimmten Users.
    """
    result = await db.execute(
        select(Game).options(selectinload(Game.throws)).where(Game.user_id == user_id)
    )
    return result.scalars().all()


async def finish_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    """
    Beende ein Spiel (setzt finished_at).
    """
    game = await get_game(db, game_id)
    if not game:
        return None

    from datetime import datetime, UTC
    game.finished_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(game)
    return game