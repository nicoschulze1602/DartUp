from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.friendship import Friendship
from app.schemas.friendship_schemas import FriendshipCreate
from typing import List, Optional


async def create_friendship(db: AsyncSession, data: FriendshipCreate) -> Friendship:
    friendship = Friendship(**data.dict())
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return friendship


async def get_friendships_for_user(db: AsyncSession, user_id: int) -> List[Friendship]:
    result = await db.execute(
        select(Friendship).where((Friendship.user_id1 == user_id) | (Friendship.user_id2 == user_id))
    )
    return result.scalars().all()