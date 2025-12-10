from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC
from sqlalchemy import select

from app.models.game_participant import GameParticipant
from app.models.throw import Throw

from app.crud import throw_crud, game_crud, game_participant_crud
from app.services.turn_service import TurnService
from app.services.game_engine import GameEngine
from app.schemas.throw_schemas import ThrowCreate


# ============================================================
# Helper-Funktionen (Tests dürfen diese patchen!)
# ============================================================

def apply_throw(current_score: int, value: int, multiplier: int):
    score_change = value * multiplier
    new_score = current_score - score_change

    if new_score < 0:
        return current_score, True, False
    if new_score == 0:
        return 0, False, True
    return new_score, False, False


async def get_next_player(db: AsyncSession, game_id: int, current_participant_id: int):
    participants = await db.scalars(
        select(GameParticipant)
        .where(GameParticipant.game_id == game_id)
        .order_by(GameParticipant.id)
    )
    ids = [p.id for p in participants]

    if current_participant_id not in ids:
        return None

    idx = ids.index(current_participant_id)
    return ids[(idx + 1) % len(ids)]


async def save_throw(db: AsyncSession, throw: Throw):
    db.add(throw)
    await db.commit()
    await db.refresh(throw)
    return throw


# ============================================================
# Hauptservice
# ============================================================

class ThrowService:

    @staticmethod
    async def process_throw(db: AsyncSession, data: ThrowCreate):

        game = await game_crud.get_game(db, data.game_id)
        if not game:
            raise ValueError("Game not found")

        participant = await game_participant_crud.get_participant(db, data.participant_id)
        if not participant:
            raise ValueError("Participant not found")

        previous_throws = await throw_crud.get_throws_for_participant(
            db, data.game_id, data.participant_id
        )

        turn_info = TurnService.get_throw_position(previous_throws)

        new_throw = await throw_crud.create_throw(
            db=db,
            game_id=data.game_id,
            participant_id=data.participant_id,
            value=data.value,
            multiplier=data.multiplier,
            turn_number=turn_info["turn_number"],
            throw_number_in_turn=turn_info["throw_number"],
            darts_thrown=turn_info["darts_thrown"],
            timestamp=datetime.now(UTC)
        )

        engine_result = GameEngine.apply_throw(
            game=game,
            participant=participant,
            throw=new_throw
        )

        next_player_name = TurnService.handle_player_switch(
            game=game,
            participant=participant,
            throw_result=engine_result["status"],
            throw_number_in_turn=turn_info["throw_number"]
        )

        await game_crud.update_game(db, game)

        return {
            "throw": new_throw,
            "player": participant.user.username,
            "remaining": participant.current_score,
            "status": engine_result["status"],
            "throw_in_turn": f"{turn_info['throw_number']}/3",
            "darts_thrown": turn_info["darts_thrown"],
            "next": next_player_name,
        }