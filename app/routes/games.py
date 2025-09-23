from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.schemas.game_schemas import GameCreate, GameOut, GameScoreboardOut, ParticipantScoreOut
from app.crud.game_crud import create_game, get_game, get_games_by_user, finish_game
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.auth.auth_utils import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)


@router.post("/start", response_model=GameOut)
async def start_game(
    game_data: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Starte ein neues Spiel.
    - Starter ist automatisch der eingeloggte User (aus Token).
    - Gegner wird über `opponent_id` angegeben.
    """
    try:
        return await create_game(db, game_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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


@router.get("/{game_id}/scoreboard", response_model=GameScoreboardOut)
async def get_scoreboard(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Gibt den aktuellen Spielstand (Scoreboard) aller Teilnehmer zurück.
    """
    # Spiel laden
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalars().first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Teilnehmer + User laden
    result = await db.execute(
        select(GameParticipant, User)
        .join(User, GameParticipant.user_id == User.id)
        .where(GameParticipant.game_id == game_id)
    )
    participants = result.all()

    # Scoreboard bauen (Pydantic-kompatibel)
    scoreboard = [
        ParticipantScoreOut(
            user_id=user.id,
            username=user.username,
            current_score=participant.current_score,
            starting_score=participant.starting_score,
            finish_order=participant.finish_order,
        )
        for participant, user in participants
    ]

    return GameScoreboardOut(
        game_id=game.id,
        status=game.status,
        start_time=game.start_time,
        end_time=game.end_time,
        participants=scoreboard
    )