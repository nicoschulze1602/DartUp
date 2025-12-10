from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GameParticipant(Base):
    """
    Verknüpft einen User mit einem Game.
    Speichert aktuellen Score + Reihenfolge + Timestamps.
    """
    __tablename__ = "game_participants"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    starting_score = Column(Integer, nullable=False)
    current_score = Column(Integer, nullable=False)
    finish_order = Column(Integer, nullable=True)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    game = relationship("Game", back_populates="participants", lazy="selectin")
    user = relationship("User", back_populates="participants", lazy="selectin")
    throws = relationship("Throw", back_populates="participant", cascade="all, delete-orphan", lazy="selectin")