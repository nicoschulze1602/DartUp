from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.services.turn_service import TurnService
from app.services.throw_validation_service import ValidationService
from app.services.game_engine import GameEngine
from app.schemas.throw_schemas import ThrowCreate
from typing import List


async def create_throw(db: AsyncSession, throw_data: ThrowCreate):
    try:
        ValidationService.validate_throw(throw_data.value, throw_data.multiplier)
    except ValueError as e:
        return None, str(e)
    # Game + Participant laden
    game = await db.get(Game, throw_data.game_id)
    participant = await db.get(GameParticipant, throw_data.participant_id)

    if not game or not participant:
        return None, "Game or participant not found"

    # Alle bisherigen Würfe laden
    result = await db.execute(
        select(Throw)
        .where(Throw.game_id == throw_data.game_id)
        .where(Throw.participant_id == throw_data.participant_id)
        .order_by(Throw.turn_number, Throw.throw_number_in_turn)
    )
    previous_throws = result.scalars().all()

    # Turn & Wurf-Nummer berechnen
    turn_number, throw_number_in_turn, darts_thrown = TurnService.get_throw_position(previous_throws)

    new_throw = Throw(
        game_id=throw_data.game_id,
        participant_id=throw_data.participant_id,
        value=throw_data.value,
        multiplier=throw_data.multiplier,
        turn_number=turn_number,
        throw_number_in_turn=throw_number_in_turn
    )

    # Spiellogik anwenden
    result = GameEngine.apply_throw(game, participant, new_throw)

    db.add(new_throw)
    await db.commit()
    await db.refresh(new_throw)
    await db.refresh(participant)

    # Nächster Spieler berechnen
    next_player = TurnService.get_next_player(game, participant, result["status"], throw_number_in_turn)

    response = {
        "player": participant.user.username,
        "last_score": new_throw.value * new_throw.multiplier,
        "remaining": participant.current_score,
        "status": result["status"],
        "throw_in_turn": f"{throw_number_in_turn}/3",
        "darts_thrown": darts_thrown,
        "next": next_player
    }

    return response

async def get_throws_by_game(db: AsyncSession, game_id: int) -> List[Throw]:
    result = await db.execute(select(Throw).where(Throw.game_id == game_id))
    return result.scalars().all()