from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Literal


# ---------- Eingabe-Schema ----------
class GameCreate(BaseModel):
    """
    Eingabe beim Erstellen eines neuen Spiels.
    """
    game_mode_id: int
    opponent_ids: List[int]                # IDs der Gegenspieler
    first_shot: Literal["host", "random", "opponent"] = "host"
    first_to: int = 1                      # Anzahl der Spiele z. B. Best-of-X


# ---------- Teilnehmer im Scoreboard ----------
class ParticipantInGame(BaseModel):
    participant_id: int
    user_id: int
    username: str
    current_score: int
    score_last_turn: Optional[int] = None
    dart1_score: Optional[int] = None
    dart2_score: Optional[int] = None
    dart3_score: Optional[int] = None
    new_score: int
    checkout_suggestion: Optional[str] = None

    # Live-Statistiken
    three_dart_average: Optional[float] = None
    first_9_average: Optional[float] = None
    highest_score: Optional[int] = None
    checkout_percentage: Optional[float] = None
    best_leg: Optional[int] = None

    class Config:
        from_attributes = True


# ---------- Ausgabe-Schema ----------
class GameOut(BaseModel):
    id: int
    game_mode_id: int
    user_id: int
    first_shot: str
    first_to: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[ParticipantInGame] = []

    class Config:
        from_attributes = True



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