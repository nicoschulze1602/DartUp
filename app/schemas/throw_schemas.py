from pydantic import BaseModel
from typing import Optional


# ---------- Basis ----------
class ThrowBase(BaseModel):
    value: int
    multiplier: int


# ---------- Eingabe ----------
class ThrowCreate(ThrowBase):
    game_id: int
    participant_id: int


# ---------- Ausgabe ----------
class ThrowOut(ThrowBase):
    id: int
    game_id: int
    participant_id: int
    score: int
    turn_number: int
    throw_number_in_turn: int

    class Config:
        from_attributes = True


# ---------- API-Response nach erfolgreichem Wurf ----------
class ThrowResponse(BaseModel):
    """
    Ausgabe eines Wurfs nach Spiellogik-Anwendung.
    """
    throw: ThrowOut                     # der gespeicherte Wurf
    player: str                         # Name des Spielers
    remaining: int                      # verbleibender Score
    status: str                         # "OK", "BUST", "WIN"
    throw_in_turn: str                  # z. B. "2/3"
    darts_thrown: int                   # bisherige Dartanzahl im Spiel
    next: str                           # nächster Spieler (Name oder "nächster Dart")

    class Config:
        from_attributes = True