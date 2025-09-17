from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ---------- Gemeinsame Basis ----------
class GameBase(BaseModel):
    game_mode_id: int  # FK zu game_modes


# ---------- Eingabe-Schema ----------
class GameCreate(GameBase):
    starter_id: int  # User, der das Spiel erstellt


# ---------- Ausgabe-Schema ----------
class GameOut(GameBase):
    """
    Response-Schema für die API.
    """
    id: int
    user_id: int
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True