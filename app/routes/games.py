from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.user import User
from app.models.game_mode import GameMode
from app.auth.auth_utils import get_current_user
from app.services.game_service import start_game
from app.services.checkout_service import get_checkout_suggestion
from app.services.game_statistics_service import GameStatisticsService
from app.schemas.game_schemas import GameCreate, GameOut, GameScoreboardOut, ParticipantInGame
from app.crud.game_crud import get_game, get_games_by_user, finish_game


router = APIRouter(prefix="/games", tags=["Games"])


# 🟩 1. Neues Spiel starten
@router.post("/start", response_model=GameOut)
async def start_new_game(
    data: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Erstellt ein neues Spiel, legt alle Teilnehmer an und gibt das Spiel mit Scoreboard zurück.
    """
    # 1. GameMode prüfen
    game_mode = await db.get(GameMode, data.game_mode_id)
    if not game_mode:
        raise HTTPException(status_code=404, detail="GameMode not found")

    # 2. Spiel starten
    game = await start_game(
        db=db,
        host=current_user,
        game_mode=game_mode,
        opponent_ids=data.opponent_ids,
        first_to=data.first_to,
        first_shot=data.first_shot
    )

    # 3. Teilnehmer aus der DB mit User-Daten laden (explizit)
    result = await db.execute(
        select(GameParticipant)
        .options(selectinload(GameParticipant.user))
        .where(GameParticipant.game_id == game.id)
    )
    participants_in_db = result.scalars().all()

    # 4. Teilnehmer für Ausgabe zusammenbauen
    participants_out = []
    for p in participants_in_db:
        username = p.user.username if p.user else "Unknown"

        participants_out.append(
            ParticipantInGame(
                participant_id=p.id,
                username=username,
                user_id=p.user_id,
                current_score=p.current_score,
                score_last_turn=None,
                dart1_score=None,
                dart2_score=None,
                dart3_score=None,
                new_score=p.current_score,
                checkout_suggestion=None,  # optional beim Start leer
                three_dart_average=0,
                first_9_average=0,
                highest_score=0,
                checkout_percentage=0,
                best_leg=None
            )
        )

    # 5. Rückgabe im gewünschten Format
    return GameOut(
        id=game.id,
        game_mode_id=game.game_mode_id,
        user_id=game.user_id,
        first_shot=game.first_shot,
        first_to=game.first_to,
        status=game.status,
        start_time=game.start_time,
        end_time=game.end_time,
        participants=participants_out
    )


# 🟨 2. Einzelnes Spiel abrufen
@router.get("/{game_id}", response_model=GameOut)
async def read_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole ein Spiel per ID.
    """
    game = await get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


# 🟦 3. Spiele eines Users abrufen
@router.get("/user/{user_id}", response_model=List[GameOut])
async def read_games_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole alle Spiele eines bestimmten Users.
    """
    return await get_games_by_user(db, user_id)


# 🟥 4. Spiel beenden
@router.put("/{game_id}/finish", response_model=GameOut)
async def finish_game_endpoint(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Beende ein Spiel (setzt end_time und Status auf 'finished').
    """
    game = await finish_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


# 🟦 5. Aktuelles Scoreboard abrufen
@router.get("/{game_id}/scoreboard", response_model=GameScoreboardOut)
async def get_scoreboard(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Gibt den aktuellen Spielstand (Scoreboard) aller Teilnehmer zurück.
    """
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.participants).selectinload(GameParticipant.user))
        .options(selectinload(Game.participants).selectinload(GameParticipant.throws))
        .where(Game.id == game_id)
    )
    game = result.scalars().first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    participants = []

    for p in game.participants:
        stats = GameStatisticsService.calculate_live_stats(p, p.throws)

        participants.append(
            ParticipantInGame(
                participant_id=p.id,
                username=p.user.username,
                user_id=p.user.id,
                current_score=p.current_score,
                score_last_turn=None,
                dart1_score=None,
                dart2_score=None,
                dart3_score=None,
                new_score=p.current_score,
                checkout_suggestion=get_checkout_suggestion(p.current_score) if p.current_score <= 170 else None,
                **stats
            )
        )

    return GameScoreboardOut(
        game_id=game.id,
        status=game.status,
        start_time=game.start_time,
        end_time=game.end_time,
        participants=participants
    )