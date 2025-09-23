from pydantic import BaseModel
from typing import Optional


# ---------- Basis ----------
class GameParticipantBase(BaseModel):
    starting_score: int
    current_score: int
    finish_order: Optional[int] = None


# ---------- Eingabe ----------
class GameParticipantCreate(GameParticipantBase):
    game_id: int
    user_id: int


# ---------- Ausgabe ----------
class GameParticipantOut(GameParticipantBase):
    id: int
    game_id: int
    user_id: int

    class Config:
        from_attributes = True