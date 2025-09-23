# ---------- Basis ----------
from pydantic import BaseModel, field_validator
from datetime import datetime


class ThrowBase(BaseModel):
    value: int  # 1-20 oder 25
    multiplier: int  # 1=Single, 2=Double, 3=Triple

    @field_validator("value")
    def validate_value(cls, v):
        if v not in list(range(1, 21)) + [25]:
            raise ValueError("Wurf muss zwischen 1–20 oder 25 (Bull) liegen")
        return v

    @field_validator("multiplier")
    def validate_multiplier(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("Multiplier muss 1 (Single), 2 (Double) oder 3 (Triple) sein")
        return v

    @field_validator("multiplier")
    def validate_bull(cls, v, values):
        # Wenn value=25, darf multiplier nur 1 oder 2 sein
        if "value" in values and values["value"] == 25 and v == 3:
            raise ValueError("Bull (25) darf kein Triple haben")
        return v


# ---------- Eingabe ----------
class ThrowCreate(ThrowBase):
    """
    Eingabe-Schema beim Speichern eines Wurfs.
    """
    game_id: int  # Zugehöriges Spiel
    user_id: int  # Welcher Spieler hat geworfen?


# ---------- Ausgabe ----------
class ThrowOut(ThrowBase):
    """
    Ausgabe-Schema für die API.
    """
    id: int
    game_id: int
    participant_id: int
    turn_number: int
    throw_number_in_turn: int
    created_at: datetime

    class Config:
        from_attributes = True