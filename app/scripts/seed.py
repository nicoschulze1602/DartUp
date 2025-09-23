import asyncio
from app.database import init_db, get_db
from app.crud.user_crud import create_user
from app.crud.game_mode_crud import create_game_mode
from app.schemas.game_mode_schemas import GameModeCreate


async def seed_data():
    """
    Initialisiert die DB und fügt Standarddaten (GameModes + User) ein.
    """
    print("Starte Seeding-Prozess...")

    # 1. DB zurücksetzen
    await init_db()
    print("✅ Datenbank zurückgesetzt und Tabellen neu erstellt.")

    async for db in get_db():
        # 2. Standard-Spielmodi
        print("➕ Füge Standard-Spielmodi hinzu...")
        default_modes = [
            {"name": "501 Double Out",
             "description": "Players start with 501 points and subtract their score with each turn. "
                            "To win, a player must land exactly on zero, "
                            "and the final dart thrown must hit a double. ",
             "starting_score": 501, "scoring_type": "subtract", "checkout_rule": "double"},
            {"name": "301 Double Out",
             "description": "Players start with 301 points and subtract their score with each turn. "
                            "To win, a player must land exactly on zero, "
                            "and the final dart thrown must hit a double",
             "starting_score": 301, "scoring_type": "subtract", "checkout_rule": "double"},
            {"name": "Cricket",
             "description": "a tactical game where players must 'close' numbers 15-20 "
                            "and the bullseye by hitting each three times. After a number is closed,"
                            "any further hits on it earn points, as long as your opponent has not also closed that number. "
                            "The winner is the first player to close all required numbers and have the highest score.",
             "starting_score": 0, "scoring_type": "add", "checkout_rule": "none"},
        ]

        for mode in default_modes:
            mode_in = GameModeCreate(**mode)
            try:
                await create_game_mode(db, data=mode_in)
                print(f"   ✅ {mode['name']} hinzugefügt.")
            except Exception as e:
                print(f"   ⚠️ Fehler bei {mode['name']}: {e}")

        # 3. Test-User
        print("➕ Füge Test-Benutzer hinzu...")
        test_users = [
            {"username": "Nico", "email": "nico@example.com", "password": "12345"},
            {"username": "testuser1", "email": "test1@example.com", "password": "securepassword"},
            {"username": "testuser2", "email": "test2@example.com", "password": "securepassword"},
        ]

        for user_data in test_users:
            try:
                await create_user(
                    db,
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],  # Klartext → wird in CRUD gehasht
                )
                print(f"   ✅ Benutzer '{user_data['username']}' hinzugefügt.")
            except Exception as e:
                print(f"   ⚠️ Fehler bei Benutzer '{user_data['username']}': {e}")

        await db.commit()

    print("🎉 Seeding-Prozess abgeschlossen.")


if __name__ == "__main__":
    asyncio.run(seed_data())