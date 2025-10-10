import asyncio
import random

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.game_mode import GameMode
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.throw import Throw
from app.services.game_engine import GameEngine
from app.services.throw_validation_service import ValidationService


async def simulate_single_game(db, users, mode) -> str:
    """
    Simuliert ein einzelnes 501-Double-Out-Spiel mit realistischeren Turns (3 Darts pro Aufnahme).
    Nutzt echte DB, GameEngine & Validierung.
    Gibt den Gewinnernamen zurück.
    """
    # Neues Spiel in DB anlegen
    new_game = Game(user_id=users[0].id, game_mode_id=mode.id, status="ongoing")
    db.add(new_game)
    await db.flush()

    participants = []
    for u in users:
        p = GameParticipant(
            game_id=new_game.id,
            user_id=u.id,
            starting_score=mode.starting_score,
            current_score=mode.starting_score,
        )
        db.add(p)
        await db.flush()
        participants.append(p)

    await db.commit()
    await db.refresh(new_game)

    # 🎯 Angepasster Wurf-Pool (mehr realistische Finishes)
    throw_values = [1, 5, 12, 16, 19, 20, 25]
    multipliers = [1, 2, 3]

    turn = 1
    winner = None
    max_turns = 120  # Sicherheitslimit für Endlosschleifen

    while not winner and turn <= max_turns:
        for participant in participants:
            if new_game.status == "finished":
                winner = participant.user.username
                break

            print(f"\n▶️ {participant.user.username} – Aufnahme {turn}")
            all_throws = []

            for dart in range(1, 4):  # bis zu 3 Darts
                value = random.choice(throw_values)
                multiplier = random.choice(multiplier := [1, 2, 3])

                try:
                    ValidationService.validate_throw(value, multiplier)
                except ValueError as e:
                    print(f"⚠️ Ungültiger Wurf: {e}")
                    continue

                throw = Throw(
                    game_id=new_game.id,
                    participant_id=participant.id,
                    value=value,
                    multiplier=multiplier,
                    turn_number=turn,
                    throw_number_in_turn=dart,
                )
                db.add(throw)
                all_throws.append(throw)

                # Spiellogik anwenden
                result = GameEngine.apply_throw(new_game, participant, throw)
                points = value * multiplier
                print(f"  Dart {dart}: {value}x{multiplier} = {points} → {result['status']}")

                if result["status"] in ["BUST", "WIN"]:
                    if result["status"] == "WIN":
                        winner = participant.user.username
                    break

            await db.commit()

            if winner:
                print(f"🏆 {winner} gewinnt!")
                new_game.status = "finished"
                await db.commit()
                break

        turn += 1

    if not winner:
        new_game.status = "aborted"
        await db.commit()
        print("\n⚠️  Simulation abgebrochen (kein Checkout nach max_turns).")

    return winner or "Niemand"


async def simulate_games(num_games: int = 3):
    """
    Führt mehrere vollständige Simulationen durch und zeigt Siegstatistik.
    """
    async with AsyncSessionLocal() as db:
        # User holen oder anlegen
        users = []
        for username in ["Alice", "Bob"]:
            result = await db.execute(
                "SELECT * FROM users WHERE username = :u", {"u": username}
            )
            row = result.fetchone()
            if not row:
                new_user = User(
                    username=username,
                    email=f"{username.lower()}@example.com",
                    password_hash="demo"
                )
                db.add(new_user)
                await db.flush()
                users.append(new_user)
            else:
                users.append(await db.get(User, row.id))

        # GameMode laden
        mode = await db.get(GameMode, 1)
        if not mode:
            raise ValueError("⚠️ Kein GameMode mit ID 1 gefunden (bitte seed_data laufen lassen)")

        stats = {u.username: 0 for u in users}

        for i in range(num_games):
            print(f"\n🎮 --- Starte Spiel {i + 1} ---")
            winner = await simulate_single_game(db, users, mode)
            if winner in stats:
                stats[winner] += 1

        print("\n📊 Endstand nach", num_games, "Spielen:")
        for user, wins in stats.items():
            print(f"  {user}: {wins} Siege")


if __name__ == "__main__":
    asyncio.run(simulate_games(3))