from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.game_mode import GameMode
from app.schemas.game_mode_schemas import GameModeCreate, GameModeOut
from app.crud.game_mode_crud import create_game_mode, get_game_mode, get_all_game_modes

router = APIRouter(tags=["Game Modes"])


@router.post("/", response_model=GameModeOut)
async def add_game_mode(data: GameModeCreate, db: AsyncSession = Depends(get_db)):
    return await create_game_mode(db, data)


@router.post("/init-defaults")
async def init_default_modes(db: AsyncSession = Depends(get_db)):
    defaults = [
        {"name": "501 Double Out", "description": "Start 501, subtract, checkout double", "starting_score": 501, "scoring_type": "subtract", "checkout_rule": "double"},
        {"name": "301 Double Out", "description": "Start 301, subtract, checkout double", "starting_score": 301, "scoring_type": "subtract", "checkout_rule": "double"},
        {"name": "Cricket", "description": "Close numbers 15-20 and bull", "starting_score": 0, "scoring_type": "add", "checkout_rule": "none"},
    ]
    for mode in defaults:
        gm = GameMode(**mode)
        db.add(gm)
    await db.commit()
    return {"message": "Default game modes added."}


@router.get("/{mode_id}", response_model=GameModeOut)
async def read_game_mode(mode_id: int, db: AsyncSession = Depends(get_db)):
    mode = await get_game_mode(db, mode_id)
    if not mode:
        raise HTTPException(status_code=404, detail="Game mode not found")
    return mode


@router.get("/", response_model=List[GameModeOut])
async def read_all_modes(db: AsyncSession = Depends(get_db)):
    return await get_all_game_modes(db)