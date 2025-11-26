from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game_participant import GameParticipant


# -------------------------------
# CREATE
# -------------------------------
async def create_participant(
    db: AsyncSession,
    game_id: int,
    user_id: int,
    starting_score: int,
) -> GameParticipant:
    """
    Legt einen neuen GameParticipant an.
    (Validierung wie 'user exists?' gehört in den Service.)
    """
    participant = GameParticipant(
        game_id=game_id,
        user_id=user_id,
        starting_score=starting_score,
        current_score=starting_score,
    )

    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


# -------------------------------
# READ: by participant_id
# -------------------------------
async def get_participant(
    db: AsyncSession,
    participant_id: int
) -> Optional[GameParticipant]:

    result = await db.execute(
        select(GameParticipant)
        .options(
            selectinload(GameParticipant.user),
            selectinload(GameParticipant.throws)
        )
        .where(GameParticipant.id == participant_id)
    )
    return result.scalars().first()


# -------------------------------
# READ: all by game_id
# -------------------------------
async def get_participants_by_game(
    db: AsyncSession,
    game_id: int
) -> List[GameParticipant]:

    result = await db.execute(
        select(GameParticipant)
        .options(
            selectinload(GameParticipant.user),
            selectinload(GameParticipant.throws),
        )
        .where(GameParticipant.game_id == game_id)
    )
    return result.scalars().unique().all()


# -------------------------------
# UPDATE: Participant speichern
# -------------------------------
async def update_participant(
    db: AsyncSession,
    participant: GameParticipant
) -> GameParticipant:

    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant

async def get_participant_by_game_and_user(
    db: AsyncSession,
    game_id: int,
    user_id: int
) -> GameParticipant | None:
    """
    Holt genau *einen* Participant basierend auf Spiel + User.
    Wird für den GameService benötigt.
    """
    result = await db.execute(
        select(GameParticipant)
        .options(selectinload(GameParticipant.user))
        .where(GameParticipant.game_id == game_id)
        .where(GameParticipant.user_id == user_id)
    )
    return result.scalars().first()