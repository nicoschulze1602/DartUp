# app/routes/throw_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.throw_schemas import ThrowCreate, ThrowResponse
from app.services.throw_service import ThrowService

router = APIRouter(prefix="/throws", tags=["Throws"])


# ---------------------------------------------------------
# 🎯 1. Neuen Wurf ausführen
# ---------------------------------------------------------
@router.post("/", response_model=ThrowResponse)
async def add_throw(
    data: ThrowCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Führt einen Dart-Wurf aus:
    - Validierung
    - Turn/Throw-Berechnung
    - GameEngine anwenden
    - Throw speichern
    - Nächsten Spieler bestimmen
    - API-Response zurückgeben
    """
    result = await ThrowService.process_throw(db, data)

    if result is None:
        raise HTTPException(status_code=400, detail="Invalid throw input")

    return result


# ---------------------------------------------------------
# 📜 2. Alle Würfe eines Spiels abrufen
# ---------------------------------------------------------
@router.get("/game/{game_id}", response_model=list[ThrowResponse])
async def get_throws_for_game(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Gibt alle gespeicherten Würfe für ein Game zurück.
    (ohne Spiellogik)
    """
    throws = await ThrowService.list_throws_for_game(db, game_id)

    if not throws:
        raise HTTPException(status_code=404, detail="No throws found")

    return throws