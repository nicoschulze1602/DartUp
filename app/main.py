from fastapi import FastAPI
from app.routes import users, games, throws

app = FastAPI(
    title="DartUp API",
    description="API für Dart-Spiel (501, 301 etc.) mit Usern, Spielen und Würfen",
    version="1.0.0",
)


# ---------- Router einbinden ----------
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(games.router, prefix="/games", tags=["games"])
app.include_router(throws.router, prefix="/throws", tags=["throws"])


@app.get("/")
async def root():
    return {"message": "Willkommen bei der DartUp API! 🎯"}