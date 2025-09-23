from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.game_participant import GameParticipant
from app.schemas.game_participant_schemas import GameParticipantCreate
from typing import List, Optional


async def create_participant(db: AsyncSession, data: GameParticipantCreate) -> GameParticipant:
    participant = GameParticipant(**data.dict())
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


async def get_participant(db: AsyncSession, participant_id: int) -> Optional[GameParticipant]:
    """
    Hole einen einzelnen Teilnehmer per ID.
    """
    result = await db.execute(select(GameParticipant).where(GameParticipant.id == participant_id))
    return result.scalars().first()


async def get_participants_by_game(db: AsyncSession, game_id: int) -> List[GameParticipant]:
    result = await db.execute(select(GameParticipant).where(GameParticipant.game_id == game_id))
    return result.scalars().all()