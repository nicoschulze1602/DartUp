from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game_mode import GameMode
from app.schemas.game_mode_schemas import GameModeCreate


async def get_game_mode(db: AsyncSession, id: int) -> Optional[GameMode]:
    return await db.get(GameMode, id)


async def get_all_game_modes(db: AsyncSession) -> List[GameMode]:
    result = await db.execute(select(GameMode))
    return result.scalars().all()


async def create_game_mode(db: AsyncSession, data: GameModeCreate) -> GameMode:
    new_mode = GameMode(**data.dict())
    db.add(new_mode)
    await db.commit()
    await db.refresh(new_mode)
    return new_mode


async def update_game_mode(db: AsyncSession, mode: GameMode) -> GameMode:
    db.add(mode)
    await db.commit()
    await db.refresh(mode)
    return mode


async def delete_game_mode(db: AsyncSession, mode_id: int) -> bool:
    mode = await db.get(GameMode, mode_id)
    if not mode:
        return False
    await db.delete(mode)
    await db.commit()
    return True