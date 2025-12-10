from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.game_mode import GameMode


# Vollständiges Game inkl. Relationen
async def get_game_entity(db: AsyncSession, game_id: int) -> Optional[Game]:
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.participants).selectinload(GameParticipant.throws),
            selectinload(Game.game_mode),
        )
        .where(Game.id == game_id)
    )
    return result.scalars().first()


# --- WICHTIG ---
async def get_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    """Von Tests und Services erwartete Wrapper-Funktion."""
    return await get_game_raw(db, game_id)


async def get_game_raw(db: AsyncSession, game_id: int) -> Optional[Game]:
    return await db.get(Game, game_id)


async def get_game_with_participants(db: AsyncSession, game_id: int):
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.participants).selectinload(GameParticipant.user))
        .where(Game.id == game_id)
    )
    return result.scalars().first()


async def create_game(
    db: AsyncSession,
    host_id: int,
    game_mode_id: int,
    opponent_ids: list[int],
    first_to: int | None = None,
    first_shot: str | None = None,
    starting_user_id: int | None = None
) -> Game:

    mode: GameMode = await db.get(GameMode, game_mode_id)
    if not mode:
        raise ValueError("game_mode_id not found")

    new_game = Game(
        user_id=host_id,
        game_mode_id=game_mode_id,
        status="ongoing",
        start_time=datetime.now(timezone.utc),
        first_to=first_to,
        first_shot=first_shot,
        current_turn_user_id=starting_user_id or host_id,
    )

    db.add(new_game)
    await db.flush()

    participants = [
        GameParticipant(
            game_id=new_game.id,
            user_id=host_id,
            starting_score=mode.starting_score,
            current_score=mode.starting_score,
        )
    ]

    for oid in opponent_ids or []:
        participants.append(
            GameParticipant(
                game_id=new_game.id,
                user_id=oid,
                starting_score=mode.starting_score,
                current_score=mode.starting_score,
            )
        )

    db.add_all(participants)
    await db.commit()
    await db.refresh(new_game)
    return new_game


async def update_game(db: AsyncSession, game: Game) -> Game:
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def finish_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    game = await get_game_entity(db, game_id)
    if not game:
        return None

    game.end_time = datetime.now(timezone.utc)
    game.status = "finished"
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def get_games_by_user_entity(db: AsyncSession, user_id: int) -> List[Game]:
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.game_mode),
        )
        .where(Game.user_id == user_id)
    )
    return result.scalars().unique().all()