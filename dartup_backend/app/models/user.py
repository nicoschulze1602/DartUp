# app/models/user.py

from pydantic import BaseModel
from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

# ---------- Pydantic Models (for request/response validation) ----------

class UserBase(BaseModel):
    """
    Shared fields between input and output models.
    """
    username: str


class UserCreate(UserBase):
    """
    Model used for user registration input (includes password).
    """
    password: str


class UserOut(UserBase):
    """
    Model used to return user information to the client (excludes password).
    """
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Allows FastAPI to read data from SQLAlchemy models

# ---------- SQLAlchemy Model (for the database table) ----------

class User(Base):
    """
    SQLAlchemy model representing the 'users' table in the PostgreSQL database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))