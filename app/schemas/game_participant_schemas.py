from pydantic import BaseModel
from typing import Optional


class GameParticipantBase(BaseModel):
    starting_score: int
    current_score: int
    finish_order: Optional[int] = None


class GameParticipantCreate(GameParticipantBase):
    game_id: int
    user_id: int


class GameParticipantOut(GameParticipantBase):
    id: int
    game_id: int
    user_id: int

    class Config:
        from_attributes = True