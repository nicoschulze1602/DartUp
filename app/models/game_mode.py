from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class GameMode(Base):
    """
    SQLAlchemy model for game_modes table.
    Represents different dart game modes (e.g. 501, 301).
    """
    __tablename__ = "game_modes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # e.g. "501", "301"
    description = Column(Text, nullable=True)

    # Relationships
    games = relationship("Game", back_populates="game_mode", cascade="all, delete-orphan")
    statistics = relationship("Statistic", back_populates="game_mode", cascade="all, delete-orphan")