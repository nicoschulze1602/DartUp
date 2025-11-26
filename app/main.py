import sys, os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Import routers
from app.routes import (
    users,
    games,
    throws,
    game_modes,
    statistics,
    friendships,
    game_participants,
    game_simulation,
)

# ----------- APP CONFIG -----------
app = FastAPI(
    title="DartUp API",
    version="1.0.0",
    description="""
**DartUp API** – A modern and fully asynchronous backend for managing dart games, players, and statistics.  

This service provides structured endpoints for:
- 👤 **User Management:** Registration, authentication, and JWT-based login  
- 🎯 **Game Logic:** Create games, record throws, and calculate results  
- 📈 **Analytics:** Retrieve detailed performance and match statistics  

Built with **FastAPI**, **SQLAlchemy (async)**, and **PostgreSQL**,  
deployed via **Render** for easy scalability and continuous integration.  

For more details, explore the available endpoints below or visit the project documentation.  
"""
)

# ----------- ROUTES EINBINDEN -----------
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(throws.router, prefix="/throws", tags=["Throws"])
app.include_router(game_modes.router, prefix="/game-modes", tags=["Game Modes"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
app.include_router(friendships.router, prefix="/friendships", tags=["Friendships"])
app.include_router(game_participants.router, prefix="/participants", tags=["Participants"])
app.include_router(game_simulation.router, prefix="/game-simulation", tags=["Game Simulation"])

# ----------- ROOT ENDPOINT -----------
@app.get("/", tags=["Welcome"])
async def root():
    """
    Friendly entry point for the DartUp API 🎯
    """
    return JSONResponse(
        content={
            "message": "🎯 Welcome to the DartUp API!",
            "info": "Manage dart games, users, and statistics with ease.",
            "documentation": {
                "Swagger UI": "/docs",
                "ReDoc": "/redoc"
            },
            "version": "1.0.0",
            "status": "online"
        }
    )