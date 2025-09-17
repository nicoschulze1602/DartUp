from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Statistic(Base):
    """
    SQLAlchemy model for statistics table.
    Stores aggregated user statistics.
    """
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_mode_id = Column(Integer, ForeignKey("game_modes.id"), nullable=True)

    games_played = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    total_throws = Column(Integer, default=0, nullable=False)
    average_score_per_throw = Column(Float, default=0.0, nullable=False)
    highest_score_per_turn = Column(Integer, default=0, nullable=False)
    total_180s = Column(Integer, default=0, nullable=False)
    highest_checkout = Column(Integer, default=0, nullable=False)
    checkout_percentage = Column(Float, default=0.0, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="statistics")
    game_mode = relationship("GameMode", back_populates="statistics")