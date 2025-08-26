from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ---------- Gemeinsame Basis ----------
class GameBase(BaseModel):
    """
    Felder, die für mehrere Game-Schemas gleich sind.
    """
    mode: str  # z. B. "501", "301"


# ---------- Eingabe-Schema ----------
class GameCreate(GameBase):
    """
    Eingabe beim Erstellen eines neuen Spiels.
    """
    user_id: int  # welcher Spieler hat das Spiel gestartet?


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