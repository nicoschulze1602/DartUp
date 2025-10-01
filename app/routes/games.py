from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.schemas.game_schemas import GameCreate, GameOut, GameScoreboardOut, ParticipantInGame
from app.crud.game_crud import create_game, get_game, get_games_by_user, finish_game, selectinload
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.auth.auth_utils import get_current_user
from app.models.user import User
from app.models.game_mode import GameMode
from app.services.checkout_service import get_checkout_suggestion
from app.services.game_service import start_game

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)


@router.post("/start", response_model=GameOut)
async def start_new_game(
    data: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # GameMode laden
    game_mode = await db.get(GameMode, data.game_mode_id)
    if not game_mode:
        raise HTTPException(status_code=404, detail="GameMode not found")

    # Game + Participants anlegen
    game = await start_game(
        db=db,
        host=current_user,
        game_mode=game_mode,
        opponent_ids=data.opponent_ids,
        first_to=data.first_to,
        first_shot=data.first_shot
    )
    return game


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
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.participants).selectinload(GameParticipant.user))
        .where(Game.id == game_id)
    )
    game = result.scalars().first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    participants = []
    for p in game.participants:
        participants.append(
            ParticipantInGame(
                user_id=p.user.id,
                username=p.user.username,
                starting_score=p.starting_score,
                current_score=p.current_score,
                checkout_suggestion=get_checkout_suggestion(p.current_score) if p.current_score <= 170 else None
            )
        )

    return GameScoreboardOut(
        game_id=game.id,
        status=game.status,
        start_time=game.start_time,
        end_time=game.end_time,
        participants=participants
    )