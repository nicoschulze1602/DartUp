from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.throw_schemas import ThrowCreate, ThrowOut
from app.crud.throw_crud import create_throw, get_throws_by_game

router = APIRouter(
    prefix="/throws",
    tags=["Throws"]
)



@router.post("/", response_model=ThrowOut)
async def add_throw(throw_data: ThrowCreate, db: AsyncSession = Depends(get_db)):
    """
    Füge einen Wurf hinzu und berechne den neuen Spielstand.
    """
    new_throw, result = await create_throw(db, throw_data)

    if not new_throw:
        raise HTTPException(status_code=404, detail=result)

    # Ergebnis (Bust, Win, OK) zusätzlich in die Response
    return {
        **new_throw.__dict__,
        "status": result["status"],
        "remaining": result["remaining"]
    }


@router.get("/game/{game_id}", response_model=List[ThrowOut])
async def read_throws_for_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole alle Würfe eines bestimmten Spiels.
    """
    throws = await get_throws_by_game(db, game_id)
    if not throws:
        raise HTTPException(status_code=404, detail="No throws found for this game")
    return throws