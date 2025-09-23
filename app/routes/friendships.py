from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.friendship_schemas import FriendshipCreate, FriendshipOut
from app.crud.friendship_crud import create_friendship, get_friendships_for_user

router = APIRouter(prefix="/friendships", tags=["Friendships"])


@router.post("/", response_model=FriendshipOut)
async def add_friendship(data: FriendshipCreate, db: AsyncSession = Depends(get_db)):
    return await create_friendship(db, data)


@router.get("/user/{user_id}", response_model=List[FriendshipOut])
async def read_friendships(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_friendships_for_user(db, user_id)