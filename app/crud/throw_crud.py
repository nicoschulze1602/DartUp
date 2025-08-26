from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.throw import Throw
from app.schemas.throw_schemas import ThrowCreate
from typing import List


async def create_throw(db: AsyncSession, throw_data: ThrowCreate) -> Throw:
    new_throw = Throw(
        game_id=throw_data.game_id,
        user_id=throw_data.user_id,
        value=throw_data.value,
        multiplier=throw_data.multiplier
    )
    db.add(new_throw)
    await db.commit()
    await db.refresh(new_throw)
    return new_throw


async def get_throws_by_game(db: AsyncSession, game_id: int) -> List[Throw]:
    result = await db.execute(select(Throw).where(Throw.game_id == game_id))
    return result.scalars().all()