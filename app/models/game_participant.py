from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class GameParticipant(Base):
    """
    Table that links users to games and tracks their score.
    """
    __tablename__ = "game_participants"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    starting_score = Column(Integer, nullable=False)
    current_score = Column(Integer, nullable=False)
    finish_order = Column(Integer, nullable=True)  # 1 = Sieger, 2 = Zweiter, ...

    # Relationships
    game = relationship("Game", back_populates="participants")
    user = relationship("User", back_populates="participants")
    throws = relationship("Throw", back_populates="participant", cascade="all, delete-orphan")