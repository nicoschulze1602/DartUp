import asyncio
import random

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.game_mode import GameMode
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.throw import Throw
from app.services.game_engine import GameEngine


async def simulate_single_game(db, users, mode) -> str:
    """
    Simuliert ein einzelnes Spiel und gibt den Gewinnernamen zurück.
    """
    # Neues Spiel anlegen
    new_game = Game(user_id=users[0].id, game_mode_id=mode.id)
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

    # Würfe simulieren, bis jemand gewinnt
    turn = 1
    winner = None
    while not winner:
        for participant in participants:
            throw_value = random.choice([0, 1, 3, 5, 7, 12, 16, 19, 19, 19, 20, 20, 20, 25])   # Demo-Werte
            multiplier = random.choice([1, 2, 3])
            throw = Throw(
                game_id=new_game.id,
                participant_id=participant.id,
                value=throw_value,
                multiplier=multiplier,
                turn_number=turn,
                throw_number_in_turn=1,
            )
            db.add(throw)

            # Spiellogik anwenden
            result = GameEngine.apply_throw(new_game, participant, throw)

            print(f"{participant.user.username} wirft {throw_value}x{multiplier} → {result}")

            if result["status"] == "WIN":
                winner = participant.user.username
                break

        turn += 1
        await db.commit()

    print(f"🏆 Gewinner: {winner}")
    return winner


async def simulate_games(num_games: int = 5):
    async with AsyncSessionLocal() as db:
        # User holen oder anlegen
        users = []
        for username in ["Alice", "Bob"]:
            result = await db.execute(
                f"SELECT * FROM users WHERE username = :u", {"u": username}
            )
            row = result.fetchone()
            if not row:
                new_user = User(username=username, email=f"{username.lower()}@example.com", password_hash="demo")
                db.add(new_user)
                await db.flush()
                users.append(new_user)
            else:
                # row ist ein Row-Objekt, deshalb Zugriff über [0]
                users.append(row[0])

        # GameMode laden
        mode = await db.get(GameMode, 1)  # ID=1 = 501 Double Out
        if not mode:
            raise ValueError("Kein GameMode mit ID 1 gefunden – bitte seed_data laufen lassen!")

        # Mehrere Spiele simulieren
        stats = {u.username: 0 for u in users}
        for i in range(num_games):
            print(f"\n🎯 --- Spiel {i+1} ---")
            winner = await simulate_single_game(db, users, mode)
            stats[winner] += 1

        # Ergebnis ausgeben
        print("\n📊 Endstand nach", num_games, "Spielen:")
        for user, wins in stats.items():
            print(f"{user}: {wins} Siege")


if __name__ == "__main__":
    asyncio.run(simulate_games(10))  # z.B. 10 Spiele simulieren