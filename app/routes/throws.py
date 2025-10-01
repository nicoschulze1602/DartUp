from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.throw_schemas import ThrowCreate, ThrowOut, ThrowResponse
from app.crud.throw_crud import create_throw, get_throws_by_game

router = APIRouter(
    prefix="/throws",
    tags=["Throws"]
)


@router.post("/", response_model=ThrowResponse)
async def add_throw(throw_data: ThrowCreate, db: AsyncSession = Depends(get_db)):
    """
    Füge einen Wurf hinzu und berechne den neuen Spielstand.
    """
    response = await create_throw(db, throw_data)

    if not response:
        raise HTTPException(status_code=404, detail="Game or participant not found")

    return response


@router.get("/game/{game_id}", response_model=List[ThrowOut])
async def read_throws_for_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole alle Würfe eines bestimmten Spiels.
    """
    throws = await get_throws_by_game(db, game_id)
    if not throws:
        raise HTTPException(status_code=404, detail="No throws found for this game")
    return throws