from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Throw(Base):
    __tablename__ = "throws"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("game_participants.id"), nullable=False)

    value = Column(Integer, nullable=False)  # Punktewert, z. B. 20, 50, 0
    multiplier = Column(Integer, default=1)  # 1=Single, 2=Double, 3=Triple

    turn_number = Column(Integer, nullable=False)
    throw_number_in_turn = Column(Integer, nullable=False)
    darts_thrown = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    game = relationship("Game", back_populates="throws")
    participant = relationship("GameParticipant", back_populates="throws")