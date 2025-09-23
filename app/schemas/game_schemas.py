from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ---------- Eingabe-Schema ----------
class GameCreate(BaseModel):
    """
    Eingabe beim Erstellen eines neuen Spiels.
    """
    game_mode_id: int     # welcher Modus (z.B. 501, Cricket)
    opponent_id: int      # welcher Gegenspieler (mind. 1 Gegner)


# ---------- Ausgabe-Schema ----------
class GameOut(BaseModel):
    """
    Response-Schema für die API.
    """
    id: int
    game_mode_id: int
    starter_id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None

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
    participants: List[ParticipantScoreOut]