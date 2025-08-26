from pydantic import BaseModel
from datetime import datetime


# ---------- Basis ----------
class ThrowBase(BaseModel):
    """
    Gemeinsame Felder für Würfe.
    """
    value: int  # z. B. 20, 5, 1
    multiplier: int  # 1=Single, 2=Double, 3=Triple


# ---------- Eingabe ----------
class ThrowCreate(ThrowBase):
    """
    Eingabe-Schema beim Speichern eines Wurfs.
    """
    game_id: int  # Zugehöriges Spiel
    user_id: int  # Welcher Spieler hat geworfen?


# ---------- Ausgabe ----------
class ThrowOut(ThrowBase):
    """
    Ausgabe-Schema für die API.
    """
    id: int
    game_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True