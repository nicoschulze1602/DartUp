import asyncio
import random

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.game_mode import GameMode
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.throw import Throw

from app.services.game_engine import GameEngine

"""
Simuliert ein einzelnes Spiel über die GameEngine + CRUD-Funktionen (umgeht Auth & API!):
1.	Erstellt 2 User (Alice, Bob) oder nimmt vorhandene.
2.	Holt den GameMode (z. B. 501 Double Out mit ID=1).
3.	Legt ein Game + GameParticipants an.
4.	Simuliert zufällige Würfe (Wert + Multiplikator).
5.	Wendet die Logik mit GameEngine.apply_throw() an.
6.	Bricht ab, sobald jemand gewinnt → Gewinner wird ausgegeben.
"""

async def simulate_game():
    # 1) Neue DB-Session
    async with AsyncSessionLocal() as db:
        # --- Optional: DB neu erstellen ---
        # await init_db()

        # 2) Zwei Test-User holen oder anlegen
        users = []
        for username in ["Alice", "Bob"]:
            result = await db.execute(
                f"SELECT * FROM users WHERE username = :u", {"u": username}
            )
            user = result.fetchone()
            if not user:
                new_user = User(username=username, email=f"{username.lower()}@example.com", password_hash="demo")
                db.add(new_user)
                await db.flush()
                users.append(new_user)
            else:
                users.append(user)

        # 3) GameMode holen (z. B. 501)
        mode = await db.get(GameMode, 1)  # ID = 1 = 501 Double Out
        if not mode:
            raise ValueError("Kein GameMode mit ID 1 gefunden – bitte vorher seed_data laufen lassen!")

        # 4) Spiel starten
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

        print(f"Spiel gestartet: {new_game.id} ({mode.name})")
        print(f"Teilnehmer: {[u.username for u in users]}")

        # 5) Würfe simulieren, bis jemand gewinnt
        turn = 1
        winner = None
        while not winner:
            for participant in participants:
                throw_value = random.choice([0, 1, 5, 20, 25])   # Demo: paar zufällige Felder
                multiplier = random.choice([1, 2, 3])            # Single / Double / Triple
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


if __name__ == "__main__":
    asyncio.run(simulate_game())