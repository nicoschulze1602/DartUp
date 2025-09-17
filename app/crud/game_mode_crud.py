from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.game_mode import GameMode
from app.schemas.game_mode_schemas import GameModeCreate
from typing import List, Optional


async def create_game_mode(db: AsyncSession, data: GameModeCreate) -> GameMode:
    new_mode = GameMode(**data.dict())
    db.add(new_mode)
    await db.commit()
    await db.refresh(new_mode)
    return new_mode


async def get_game_mode(db: AsyncSession, mode_id: int) -> Optional[GameMode]:
    result = await db.execute(select(GameMode).where(GameMode.id == mode_id))
    return result.scalars().first()


async def get_all_game_modes(db: AsyncSession) -> List[GameMode]:
    result = await db.execute(select(GameMode))
    return result.scalars().all()