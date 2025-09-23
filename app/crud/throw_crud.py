from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.services.game_engine import GameEngine
from app.schemas.throw_schemas import ThrowCreate
from typing import List


async def create_throw(db: AsyncSession, throw_data: ThrowCreate):
    """
    Legt einen neuen Wurf an und wendet die Spiellogik an.
    """
    # Game + Participant laden
    game = await db.get(Game, throw_data.game_id)
    participant = await db.get(GameParticipant, throw_data.participant_id)

    if not game or not participant:
        return None, "Game or participant not found"

    new_throw = Throw(
        game_id=throw_data.game_id,
        participant_id=throw_data.participant_id,
        value=throw_data.value,
        multiplier=throw_data.multiplier,
        turn_number=1,  # TODO: turn handling
        throw_number_in_turn=1  # TODO: throw handling
    )

    # Spiellogik anwenden
    result = GameEngine.apply_throw(game, participant, new_throw)

    db.add(new_throw)
    await db.commit()
    await db.refresh(new_throw)
    await db.refresh(participant)  # neuen Score abrufen

    return new_throw, result

async def get_throws_by_game(db: AsyncSession, game_id: int) -> List[Throw]:
    result = await db.execute(select(Throw).where(Throw.game_id == game_id))
    return result.scalars().all()