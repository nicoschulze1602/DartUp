from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.throw import Throw


async def create_throw(
    db: AsyncSession,
    game_id: int,
    participant_id: int,
    value: int,
    multiplier: int,
    turn_number: int,
    throw_number_in_turn: int,
    darts_thrown: int,
    timestamp: Optional[datetime] = None,
) -> Throw:
    """
    Legt einen neuen Throw in der DB an und gibt das ORM-Objekt zurück.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    new_throw = Throw(
        game_id=game_id,
        participant_id=participant_id,
        value=value,
        multiplier=multiplier,
        turn_number=turn_number,
        throw_number_in_turn=throw_number_in_turn,
        darts_thrown=darts_thrown,
        timestamp=timestamp,
    )

    db.add(new_throw)
    await db.commit()
    await db.refresh(new_throw)
    return new_throw


async def get_throws_by_game(db: AsyncSession, game_id: int) -> List[Throw]:
    result = await db.execute(
        select(Throw)
        .where(Throw.game_id == game_id)
        .order_by(Throw.turn_number, Throw.throw_number_in_turn)
    )
    return result.scalars().all()


async def get_throws_for_participant(db: AsyncSession, game_id: int, participant_id: int) -> List[Throw]:
    result = await db.execute(
        select(Throw)
        .where(Throw.game_id == game_id)
        .where(Throw.participant_id == participant_id)
        .order_by(Throw.turn_number, Throw.throw_number_in_turn)
    )
    return result.scalars().all()


async def get_last_throw_for_participant(db: AsyncSession, game_id: int, participant_id: int) -> Optional[Throw]:
    """
    Liefert den letzten Throw für einen Teilnehmer (oder None).
    """
    result = await db.execute(
        select(Throw)
        .where(Throw.game_id == game_id)
        .where(Throw.participant_id == participant_id)
        .order_by(desc(Throw.turn_number), desc(Throw.throw_number_in_turn))
        .limit(1)
    )
    return result.scalars().first()


async def get_all_throws(db: AsyncSession) -> List[Throw]:
    result = await db.execute(select(Throw).order_by(Throw.game_id, Throw.turn_number, Throw.throw_number_in_turn))
    return result.scalars().all()