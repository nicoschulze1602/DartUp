from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.statistic_schemas import StatisticCreate, StatisticOut
from app.crud.statistic_crud import create_statistic, get_statistic_by_user

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.post("/", response_model=StatisticOut)
async def add_statistic(data: StatisticCreate, db: AsyncSession = Depends(get_db)):
    return await create_statistic(db, data)


@router.get("/user/{user_id}", response_model=StatisticOut)
async def read_user_statistic(user_id: int, db: AsyncSession = Depends(get_db)):
    stat = await get_statistic_by_user(db, user_id)
    if not stat:
        raise HTTPException(status_code=404, detail="Statistics not found")
    return stat