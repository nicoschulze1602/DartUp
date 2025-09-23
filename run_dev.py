import asyncio
import subprocess

from app.scripts.seed import seed_data


async def main():
    # 1. Seed-Datenbank
    print("🚀 Starte Seeding / Init-DB Script...")
    await seed_data()
    print("✅ Seeding abgeschlossen!")

    # 2. Starte den Server mit uvicorn
    print("🚀 Starte FastAPI-Server...")
    subprocess.run(["uvicorn", "app.main:app", "--reload"])


if __name__ == "__main__":
    asyncio.run(main())


