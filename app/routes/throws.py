from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.throw_schemas import ThrowCreate, ThrowResponse, ThrowOut
from app.crud.throw_crud import create_throw, get_throws_by_game

router = APIRouter(
    prefix="/throws",
    tags=["Throws"]
)


# ---------------------------------------------------------
# 🎯 Wurf ausführen
# ---------------------------------------------------------
@router.post("/", response_model=ThrowResponse)
async def add_throw(throw_data: ThrowCreate, db: AsyncSession = Depends(get_db)):
    """
    Fügt einen neuen Wurf hinzu, berechnet Position im Turn,
    prüft Sieg/Bust und gibt den neuen Spielstatus zurück.
    """
    response = await create_throw(db, throw_data)

    # Fehlerbehandlung
    if not response:
        raise HTTPException(status_code=400, detail="Invalid throw data")

    # Falls create_throw ein Tupel (None, str) zurückgibt
    if isinstance(response, tuple):
        _, error_message = response
        raise HTTPException(status_code=400, detail=error_message)

    return response


# ---------------------------------------------------------
# 📜 Alle Würfe eines Spiels abrufen
# ---------------------------------------------------------
@router.get("/game/{game_id}", response_model=List[ThrowOut])
async def read_throws_for_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Gibt alle Würfe eines bestimmten Spiels zurück.
    """
    throws = await get_throws_by_game(db, game_id)
    if not throws:
        raise HTTPException(status_code=404, detail="No throws found for this game")

    return throws