from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.game_schemas import GameCreate, GameOut
from app.crud.game_crud import create_game, get_game, get_games_by_user, finish_game

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)


@router.post("/start", response_model=GameOut)
async def start_game(game_data: GameCreate, db: AsyncSession = Depends(get_db)):
    """
    Starte ein neues Spiel für einen bestimmten User.
    """
    return await create_game(db, game_data)


@router.get("/{game_id}", response_model=GameOut)
async def read_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole ein Spiel per ID.
    """
    game = await get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/user/{user_id}", response_model=List[GameOut])
async def read_games_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole alle Spiele eines bestimmten Users.
    """
    return await get_games_by_user(db, user_id)


@router.put("/{game_id}/finish", response_model=GameOut)
async def finish_game_endpoint(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Beende ein Spiel (setzt end_time).
    """
    game = await finish_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game