from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Throw(Base):
    """
    SQLAlchemy model representing a dart throw in a game.
    """
    __tablename__ = "throws"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    value = Column(Integer, nullable=False)  # z. B. 20, 50, 0
    multiplier = Column(Integer, default=1, nullable=False)  # 1 = Single, 2 = Double, 3 = Triple

    # Beziehung zur Game-Tabelle
    game = relationship("Game", back_populates="throws")