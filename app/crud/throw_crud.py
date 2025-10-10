from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.throw import Throw
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.services.turn_service import TurnService
from app.services.throw_validation_service import ValidationService
from app.services.game_engine import GameEngine
from app.schemas.throw_schemas import ThrowCreate, ThrowOut
from typing import List


async def create_throw(db: AsyncSession, throw_data: ThrowCreate):
    """
    Fügt einen neuen Wurf hinzu, berechnet Turn-/Throw-Position
    und aktualisiert Spielstatus & Punkte.
    """

    # 1️⃣ Eingabewerte prüfen
    try:
        ValidationService.validate_throw(throw_data.value, throw_data.multiplier)
    except ValueError as e:
        return None, str(e)

    # 2️⃣ Game vollständig mit allen Abhängigkeiten laden
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.game_mode)
        )
        .where(Game.id == throw_data.game_id)
    )
    game = result.scalars().first()

    # ✅ Participant + User laden (statt db.get)
    result = await db.execute(
        select(GameParticipant)
        .options(selectinload(GameParticipant.user))
        .where(GameParticipant.id == throw_data.participant_id)
    )
    participant = result.scalars().first()

    if not game or not participant:
        return None, "Game or participant not found"

    # 🟩 Username & Participants-Daten sichern (noch vor Commit!)
    player_username = participant.user.username if participant.user else f"Teilnehmer {participant.id}"
    participants_data = [
        {"id": p.id, "username": p.user.username if p.user else f"Teilnehmer {p.id}"}
        for p in game.participants
    ]
    current_participant_data = {"id": participant.id, "username": player_username}

    # 3️⃣ Bisherige Würfe laden
    result = await db.execute(
        select(Throw)
        .where(Throw.game_id == throw_data.game_id)
        .where(Throw.participant_id == throw_data.participant_id)
        .order_by(Throw.turn_number, Throw.throw_number_in_turn)
    )
    previous_throws = result.scalars().all()

    # 4️⃣ Turn / Wurf-Nummer berechnen
    turn_number, throw_number_in_turn, darts_thrown = TurnService.get_throw_position(previous_throws)

    # 5️⃣ Neuen Wurf erstellen
    new_throw = Throw(
        game_id=throw_data.game_id,
        participant_id=throw_data.participant_id,
        value=throw_data.value,
        multiplier=throw_data.multiplier,
        turn_number=turn_number,
        throw_number_in_turn=throw_number_in_turn
    )

    # 6️⃣ Spiellogik anwenden
    result = GameEngine.apply_throw(game, participant, new_throw)

    db.add(new_throw)
    await db.commit()  # ❗ Danach keine ORM-Abfragen mehr
    await db.refresh(new_throw)
    await db.refresh(participant)
    await db.refresh(game)

    # 7️⃣ Nächsten Spieler bestimmen — jetzt nur mit Dictionaries
    next_player = TurnService.get_next_player(
        game,
        current_participant_data,
        participants_data,
        result["status"],
        throw_number_in_turn
    )

    # 8️⃣ Response-Objekt bauen
    throw_out = ThrowOut(
        id=new_throw.id,
        game_id=new_throw.game_id,
        participant_id=new_throw.participant_id,
        value=new_throw.value,
        multiplier=new_throw.multiplier,
        score=new_throw.value * new_throw.multiplier,
        turn_number=new_throw.turn_number,
        throw_number_in_turn=new_throw.throw_number_in_turn
    )

    response = {
        "throw": throw_out,
        "player": player_username,  # ✅ kein Lazy Load mehr
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