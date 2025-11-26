import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.throw import Throw
from app.services.turn_service import TurnService
from app.services.game_engine import GameEngine
from app.services.throw_validation_service import ValidationService  # ✅ für gültige Würfe
from app.schemas.game_schemas import GameScoreboardOut

router = APIRouter(tags=["Game Simulation"])


# 🧩Checkout-Helfer
def get_checkout_throw(score: int):
    """Gibt bei möglichem Finish einen gezielten Double-Versuch zurück."""
    checkout_table = {
        50: (25, 2),  # Bullseye
        40: (20, 2),
        32: (16, 2),
        24: (12, 2),
        20: (10, 2),
        16: (8, 2),
        8: (4, 2),
        2: (1, 2),
    }
    return checkout_table.get(score, None)


@router.post("/{game_id}/simulate-turn", response_model=GameScoreboardOut)
async def simulate_turn(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    🎯 Simuliert eine komplette Aufnahme (max. 3 Würfe) für den aktuellen Spieler.
    Führt danach ggf. Turnwechsel durch und gibt Debug-Infos in der Konsole aus.
    """

    # 🧠 Spiel mit Kontext laden
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.game_mode),
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.participants).selectinload(GameParticipant.throws),
        )
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 🧩 Aktuellen Teilnehmer finden
    current_participant = next(
        (p for p in game.participants if p.user_id == game.current_turn_user_id),
        None,
    )
    if not current_participant:
        raise HTTPException(status_code=404, detail="Current participant not found")

    print(f"\n🎯 --- Simuliere Turn für {current_participant.user.username} ---")

    all_throws = list(current_participant.throws or [])
    debug_log = []  # 👉 Sammeln für schöne Ausgabe
    result = {"status": "OK"}
    throw_number_in_turn = 0

    # 🏹 Simuliere bis zu 3 Würfe oder bis BUST/WIN
    for _ in range(3):
        turn_number, throw_number_in_turn, _ = TurnService.get_throw_position(all_throws)

        # 🎯 Versuche gezielten Checkout, falls möglich
        possible_checkout = get_checkout_throw(current_participant.current_score)
        if possible_checkout:
            value, multiplier = possible_checkout
        else:
            # 🧩 Zufälliger gültiger Wurf (mit Validierung)
            while True:
                value = random.choice([1, 5, 12, 16, 19, 20, 25])
                multiplier = random.choice([1, 2, 3])
                try:
                    ValidationService.validate_throw(value, multiplier)
                    break
                except ValueError:
                    continue

        throw = Throw(
            game_id=game.id,
            participant_id=current_participant.id,
            value=value,
            multiplier=multiplier,
            turn_number=turn_number,
            throw_number_in_turn=throw_number_in_turn,
        )
        db.add(throw)
        all_throws.append(throw)

        # 🔢 Spiellogik anwenden
        old_score = current_participant.current_score
        result = GameEngine.apply_throw(game, current_participant, throw)
        new_score = current_participant.current_score
        status = result["status"]

        debug_log.append(
            f"🎯 {current_participant.user.username} wirft {value}x{multiplier} = {value * multiplier} "
            f"Punkte | Score: {old_score} → {new_score} ({status})"
        )

        if status in ["BUST", "WIN"]:
            break

    # 🔁 Turnwechsel nur bei Turnende
    if result["status"] in ["BUST", "WIN"] or throw_number_in_turn == 3:
        participants = game.participants
        current_index = participants.index(current_participant)
        next_index = (current_index + 1) % len(participants)
        next_participant = participants[next_index]
        game.current_turn_user_id = next_participant.user_id
        debug_log.append(f"🔁 Nächster Spieler: {next_participant.user.username}")

    # 🏆 Spiel beenden, falls gewonnen
    if result["status"] == "WIN":
        game.status = "finished"
        debug_log.append(f"🏆 {current_participant.user.username} gewinnt das Spiel!")

    # 📊 Zwischenstand
    debug_log.append("📊 Aktueller Spielstand:")
    for p in game.participants:
        debug_log.append(f"  {p.user.username}: {p.current_score} Punkte")

    print("\n".join(debug_log))
    print("—" * 60)

    await db.commit()
    await db.refresh(game)
    return await get_scoreboard(game.id, db)


@router.post("/{game_id}/simulate-game", response_model=GameScoreboardOut)
async def simulate_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    🧩 Simuliert ein komplettes Spiel bis ein Gewinner feststeht.
    Gibt alle Aktionen als Debug-Output in der Konsole aus.
    """

    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.game_mode),
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.participants).selectinload(GameParticipant.throws),
        )
        .where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    print(f"\n🎮 --- Starte vollständige Simulation für Spiel {game.id} ---\n")

    winner = None
    scoreboard = None
    max_turns = 150
    turn_counter = 0

    while not winner and turn_counter < max_turns:
        turn_counter += 1
        print(f"\n🏁 Turn {turn_counter}")
        scoreboard = await simulate_turn(game.id, db)

        for p in scoreboard.participants:
            if p.new_score == 0:
                winner = p.username
                game.status = "finished"
                print(f"\n🏆 {winner} gewinnt das Spiel nach {turn_counter} Turns!\n")
                break

    if not winner:
        game.status = "aborted"
        print("\n⚠️  Max turn limit reached — Simulation aborted.\n")

    await db.commit()
    await db.refresh(game)
    return scoreboard