from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.game_mode_schemas import GameModeCreate, GameModeOut
from app.crud.game_mode_crud import create_game_mode, get_game_mode, get_all_game_modes

router = APIRouter(prefix="/game-modes", tags=["game modes"])


@router.post("/", response_model=GameModeOut)
async def add_game_mode(data: GameModeCreate, db: AsyncSession = Depends(get_db)):
    return await create_game_mode(db, data)


@router.get("/{mode_id}", response_model=GameModeOut)
async def read_game_mode(mode_id: int, db: AsyncSession = Depends(get_db)):
    mode = await get_game_mode(db, mode_id)
    if not mode:
        raise HTTPException(status_code=404, detail="Game mode not found")
    return mode


@router.get("/", response_model=List[GameModeOut])
async def read_all_modes(db: AsyncSession = Depends(get_db)):
    return await get_all_game_modes(db)