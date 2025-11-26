import asyncio
from app.database import init_db, AsyncSessionLocal
from app.auth.auth_utils import hash_password
from app.crud.user_crud import create_user
from app.crud.game_mode_crud import create_game_mode
from app.schemas.game_mode_schemas import GameModeCreate


async def seed_data():
    print("🚀 Starte Seeding...\n")

    # 1️⃣ Reset der Datenbank (DROP + CREATE)
    await init_db()
    print("✅ DB neu initialisiert.\n")

    # 2️⃣ Neue Session öffnen
    async with AsyncSessionLocal() as db:

        # ----------------------------------------------------
        # 🎯 Spielmodi einfügen
        # ----------------------------------------------------
        print("🎯 Füge GameModes hinzu...\n")

        modes = [
            GameModeCreate(
                name="501 Double Out",
                description="Klassischer 501-Modus mit Double-Out.",
                starting_score=501,
                scoring_type="subtract",
                checkout_rule="double"
            ),
            GameModeCreate(
                name="301 Double Out",
                description="Schnellerer 301-Modus mit Double-Out.",
                starting_score=301,
                scoring_type="subtract",
                checkout_rule="double"
            ),
            GameModeCreate(
                name="Cricket",
                description="Cricket-Modus mit Zahlen 15–20.",
                starting_score=0,
                scoring_type="add",
                checkout_rule="none"
            )
        ]

        for mode in modes:
            await create_game_mode(db, mode)
            print(f"   ➕ Added: {mode.name}")

        # ----------------------------------------------------
        # 👤 Test-User einfügen
        # ----------------------------------------------------
        print("\n👤 Füge Test-User hinzu...\n")

        seed_users = [
            ("Nico", "nico@example.com", "12345"),
            ("John", "john@example.com", "12345"),
            ("Alice", "alice@example.com", "securepass"),
        ]

        for username, email, pw in seed_users:
            await create_user(
                db,
                username=username,
                email=email,
                password_hash=hash_password(pw),
            )
            print(f"   👤 User '{username}' erstellt.")

        await db.commit()

    print("\n🎉 Seeding abgeschlossen!\n")


if __name__ == "__main__":
    asyncio.run(seed_data())