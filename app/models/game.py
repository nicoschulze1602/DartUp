from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Game(Base):
    """
    SQLAlchemy model representing a dart game.
    """
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mode = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Beziehungen
    user = relationship("User", back_populates="games")
    throws = relationship("Throw", back_populates="game", cascade="all, delete-orphan")