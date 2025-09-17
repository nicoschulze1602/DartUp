from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FriendshipBase(BaseModel):
    status: str = "pending"


class FriendshipCreate(FriendshipBase):
    user_id1: int
    user_id2: int


class FriendshipOut(FriendshipBase):
    id: int
    user_id1: int
    user_id2: int
    created_at: datetime
    accepted_at: Optional[datetime]

    class Config:
        from_attributes = True