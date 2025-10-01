from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---------- Basis ----------
class GameParticipantBase(BaseModel):
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
    joined_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True