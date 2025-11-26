from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.auth.auth_utils import get_current_user
from app.models.user import User
from app.models.game_mode import GameMode
from app.schemas.game_schemas import GameCreate, GameOut
from app.services.game_service import GameService
from app.crud.game_crud import get_games_by_user_entity

router = APIRouter(prefix="/games", tags=["Games"])


# -------------------------------------------------------------
# 1. Neues Spiel starten
# -------------------------------------------------------------
@router.post("/start", response_model=GameOut)
async def start_new_game(
    data: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Erstellt ein neues Spiel und gibt die initialen Spielinformationen zurück.
    """

    # GameMode holen
    game_mode = await db.get(GameMode, data.game_mode_id)
    if not game_mode:
        raise HTTPException(status_code=404, detail="GameMode not found")

    # GameService nutzt das CRUD sauber
    game = await GameService.start_game(
        db=db,
        host=current_user,
        game_mode=game_mode,
        opponent_ids=data.opponent_ids,
        first_to=data.first_to,
        first_shot=data.first_shot
    )

    return game


# -------------------------------------------------------------
# 2. Spiel abrufen
# -------------------------------------------------------------
@router.get("/{game_id}", response_model=GameOut)
async def read_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lädt ein Spiel inklusive Prüfungen, ob der User teilnehmen darf.
    """
    game, participant = await GameService.load_game(db, game_id, current_user.id)
    return game   # Nur das Spiel zurückgeben


# -------------------------------------------------------------
# 3. Spiele eines Users
# -------------------------------------------------------------
@router.get("/user/{user_id}", response_model=List[GameOut])
async def read_games_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Liste aller Spiele eines Users.
    """
    return await get_games_by_user_entity(db, user_id)


# -------------------------------------------------------------
# 4. Spiel beenden
# -------------------------------------------------------------
@router.put("/{game_id}/finish", response_model=GameOut)
async def finish_game_endpoint(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endet ein Spiel (setzt Status + Endzeit).
    Nur Spieler im Game dürfen dies tun.
    """

    # Sicherheits-check: User muss Teilnehmer sein
    await GameService.load_game(db, game_id, current_user.id)

    return await GameService.finish_game(db, game_id)