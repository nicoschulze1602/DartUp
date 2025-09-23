from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.game_participant_schemas import GameParticipantCreate, GameParticipantOut
from app.crud.game_participant_crud import create_participant, get_participant, get_participants_by_game

router = APIRouter(prefix="/participants", tags=["Participants"])


@router.post("/", response_model=GameParticipantOut)
async def add_participant(data: GameParticipantCreate, db: AsyncSession = Depends(get_db)):
    return await create_participant(db, data)


@router.get("/{participant_id}", response_model=GameParticipantOut)
async def read_participant(participant_id: int, db: AsyncSession = Depends(get_db)):
    participant = await get_participant(db, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant


@router.get("/game/{game_id}", response_model=List[GameParticipantOut])
async def read_participants(game_id: int, db: AsyncSession = Depends(get_db)):
    return await get_participants_by_game(db, game_id)