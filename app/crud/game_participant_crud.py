from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.game_participant import GameParticipant
from app.schemas.game_participant_schemas import GameParticipantCreate
from typing import List, Optional


async def create_participant(db: AsyncSession, data: GameParticipantCreate) -> GameParticipant:
    """
    Erstellt einen neuen Teilnehmer in der Datenbank.
    """
    participant = GameParticipant(**data.dict())
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


async def get_participant(db: AsyncSession, participant_id: int) -> Optional[GameParticipant]:
    """
    Holt einen einzelnen Teilnehmer inkl. zugehörigem User & Throws.
    """
    result = await db.execute(
        select(GameParticipant)
        .options(
            selectinload(GameParticipant.user),
            selectinload(GameParticipant.throws)
        )
        .where(GameParticipant.id == participant_id)
    )
    return result.scalars().first()


async def get_participants_by_game(db: AsyncSession, game_id: int) -> List[GameParticipant]:
    """
    Holt alle Teilnehmer eines Spiels inkl. zugehörigem User & Throws.
    """
    result = await db.execute(
        select(GameParticipant)
        .options(
            selectinload(GameParticipant.user),
            selectinload(GameParticipant.throws)
        )
        .where(GameParticipant.game_id == game_id)
    )
    return result.scalars().all()