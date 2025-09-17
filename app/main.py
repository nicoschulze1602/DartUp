import sys, os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI

# Import routers
from app.routes import (
    users,
    games,
    throws,
    game_modes,
    statistics,
    friendships,
    game_participants,
)

# ----------- APP CONFIG -----------
app = FastAPI(
    title="DartUp API",
    version="1.0.0",
    description="🎯 API for managing dart games, users, and statistics."
)

# ----------- ROUTES EINBINDEN -----------
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(throws.router, prefix="/throws", tags=["Throws"])
app.include_router(game_modes.router, prefix="/game-modes", tags=["Game Modes"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
app.include_router(friendships.router, prefix="/friendships", tags=["Friendships"])
app.include_router(game_participants.router, prefix="/participants", tags=["Participants"])

# ----------- ROOT ENDPOINT -----------
@app.get("/", tags=["Root"])
async def root():
    return {"message": "🎯 Welcome to DartUp API! Visit /docs for Swagger UI."}