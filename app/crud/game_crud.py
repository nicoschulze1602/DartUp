from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, UTC

from app.models.user import User
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.game_mode import GameMode
from app.schemas.game_schemas import GameCreate


async def create_game(db: AsyncSession, game_data: GameCreate, current_user: User) -> Game:
    """
    Neues Spiel in der DB anlegen + alle Participants erzeugen.
    """
    # 1. GameMode laden
    result = await db.execute(select(GameMode).where(GameMode.id == game_data.game_mode_id))
    mode = result.scalars().first()
    if not mode:
        raise ValueError("Invalid game_mode_id")

    # 2. Neues Spiel anlegen
    new_game = Game(
        user_id=current_user.id,     # Host = eingeloggter User
        game_mode_id=game_data.game_mode_id,
        status="ongoing"
    )
    db.add(new_game)
    await db.flush()

    # 3. Participants anlegen
    participants = []

    # Host
    participants.append(GameParticipant(
        game_id=new_game.id,
        user_id=current_user.id,
        starting_score=mode.starting_score,
        current_score=mode.starting_score
    ))

    # Gegner
    for opp_id in game_data.opponent_ids:
        participants.append(GameParticipant(
            game_id=new_game.id,
            user_id=opp_id,
            starting_score=mode.starting_score,
            current_score=mode.starting_score
        ))

    db.add_all(participants)

    # 4. Alles speichern
    await db.commit()
    await db.refresh(new_game)

    result = await db.execute(
        select(Game).options(
            selectinload(Game.participants).selectinload(GameParticipant.user)
        ).where(Game.id == new_game.id)
    )
    return result.scalars().first()


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