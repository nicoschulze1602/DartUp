from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.game_participant_schemas import GameParticipantCreate, GameParticipantOut
from app.crud.game_participant_crud import (
    create_participant,
    get_participant,
    get_participants_by_game
)

router = APIRouter(tags=["Participants"])


@router.post("/", response_model=GameParticipantOut)
async def add_participant(data: GameParticipantCreate, db: AsyncSession = Depends(get_db)):
    """
    Fügt einen neuen Teilnehmer zu einem Spiel hinzu.
    """
    participant = await create_participant(db, data)
    return GameParticipantOut(
        id=participant.id,
        game_id=participant.game_id,
        user_id=participant.user_id,
        username=participant.user.username if participant.user else None,
        current_score=participant.current_score,
        finish_order=participant.finish_order,
        joined_at=participant.joined_at,
        finished_at=participant.finished_at
    )


@router.get("/{participant_id}", response_model=GameParticipantOut)
async def read_participant(participant_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole einen einzelnen Teilnehmer inkl. Username.
    """
    participant = await get_participant(db, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return GameParticipantOut(
        id=participant.id,
        game_id=participant.game_id,
        user_id=participant.user_id,
        username=participant.user.username if participant.user else None,
        current_score=participant.current_score,
        finish_order=participant.finish_order,
        joined_at=participant.joined_at,
        finished_at=participant.finished_at
    )


@router.get("/game/{game_id}", response_model=List[GameParticipantOut])
async def read_participants_for_game(game_id: int, db: AsyncSession = Depends(get_db)):
    """
    Hole alle Teilnehmer eines bestimmten Spiels inkl. Username und Scores.
    """
    participants = await get_participants_by_game(db, game_id)
    if not participants:
        raise HTTPException(status_code=404, detail="No participants found")

    return [
        GameParticipantOut(
            id=p.id,
            game_id=p.game_id,
            user_id=p.user_id,
            username=p.user.username if p.user else None,
            current_score=p.current_score,
            finish_order=p.finish_order,
            joined_at=p.joined_at,
            finished_at=p.finished_at
        )
        for p in participants
    ]