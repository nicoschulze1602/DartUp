from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StatisticBase(BaseModel):
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    total_throws: int = 0
    average_score_per_throw: float = 0.0
    highest_score_per_turn: int = 0
    total_180s: int = 0
    highest_checkout: int = 0
    checkout_percentage: float = 0.0


class StatisticCreate(StatisticBase):
    user_id: int
    game_mode_id: Optional[int] = None


class StatisticOut(StatisticBase):
    id: int
    user_id: int
    game_mode_id: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True