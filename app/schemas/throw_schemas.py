from pydantic import BaseModel
from datetime import datetime


# ---------- Basis ----------
class ThrowBase(BaseModel):
    value: int  # 1-20 oder 25
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
    Ausgabe-Schema für die API (alle gespeicherten Würfe).
    """
    id: int
    game_id: int
    participant_id: int
    turn_number: int
    throw_number_in_turn: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Erweiterte API-Response ----------
class ThrowResponse(BaseModel):
    """
    Antwort nach einem neuen Wurf – incl. Status und Spiellogik.
    """
    player: str
    last_score: int
    remaining: int
    status: str  # OK, BUST, WIN
    throw_in_turn: str  # z.B. "2/3"
    darts_thrown: int
    next: str