from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ---------- Eingabe-Schema ----------
class GameCreate(BaseModel):
    """
    Eingabe beim Erstellen eines neuen Spiels.
    """
    game_mode_id: int
    opponent_ids: List[int]     # IDs der Gegenspieler
    first_shot: Optional[str] = "host"  # host | random | opponent
    first_to: Optional[int] = 1         # z. B. Best-of-X


# ---------- Ausgabe-Schema ----------
class ParticipantInGame(BaseModel):
    user_id: int
    username: str
    starting_score: int
    current_score: int
    checkout_suggestion: Optional[str] = None

    class Config:
        from_attributes = True


class GameOut(BaseModel):
    id: int
    game_mode_id: int
    user_id: int  # Host
    first_shot: str
    first_to: int

    class Config:
        from_attributes = True


# ---------- Scoreboard ----------
class ParticipantScoreOut(BaseModel):
    """
    Einzelner Teilnehmer im Scoreboard (Ausgabe).
    """
    user_id: int
    username: str
    current_score: int
    starting_score: int
    finish_order: Optional[int] = None


class GameScoreboardOut(BaseModel):
    """
    Gesamtübersicht für das Scoreboard eines Spiels.
    """
    game_id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[ParticipantInGame]

    class Config:
        from_attributes = True