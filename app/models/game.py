from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Starter/Owner
    game_mode_id = Column(Integer, ForeignKey("game_modes.id"), nullable=False)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(String, nullable=False, default="ongoing")
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="games", foreign_keys=[user_id])   # Starter
    winner = relationship("User", foreign_keys=[winner_id])                       # Sieger
    participants = relationship("GameParticipant", back_populates="game", cascade="all, delete-orphan")
    throws = relationship("Throw", back_populates="game", cascade="all, delete-orphan")
    game_mode = relationship("GameMode", back_populates="games")
