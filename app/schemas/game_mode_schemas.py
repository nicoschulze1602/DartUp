from pydantic import BaseModel
from typing import Optional


class GameModeBase(BaseModel):
    name: str
    description: Optional[str] = None
    starting_score: Optional[int] = None
    scoring_type: str  # "subtract" oder "add"
    checkout_rule: Optional[str] = None  # "double", "straight", None


class GameModeCreate(GameModeBase):
    pass


class GameModeOut(GameModeBase):
    id: int

    class Config:
        from_attributes = True