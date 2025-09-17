from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ---------- Gemeinsame Basis ----------
class UserBase(BaseModel):
    """
    Felder, die in mehreren User-Schemas geteilt werden.
    """
    username: str
    email: EmailStr  # <--- Email jetzt Teil der Basis


# ---------- Eingabe-Schemas ----------
class UserCreate(UserBase):
    """
    Wird beim Registrieren eines neuen Users genutzt.
    """
    password: str


class UserLogin(BaseModel):
    """
    Wird beim Login genutzt.
    """
    username: str
    password: str


# ---------- Ausgabe-Schemas ----------
class UserOut(UserBase):
    """
    Response-Model für den Client (ohne Passwort).
    """
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # macht SQLAlchemy-Model mit Pydantic kompatibel