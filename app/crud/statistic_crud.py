from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.statistic import Statistic
from app.schemas.statistic_schemas import StatisticCreate
from typing import Optional


async def create_statistic(db: AsyncSession, data: StatisticCreate) -> Statistic:
    stat = Statistic(**data.dict())
    db.add(stat)
    await db.commit()
    await db.refresh(stat)
    return stat


async def get_statistic_by_user(db: AsyncSession, user_id: int) -> Optional[Statistic]:
    result = await db.execute(select(Statistic).where(Statistic.user_id == user_id))
    return result.scalars().first()