from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, UTC


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    game_mode_id = Column(Integer, ForeignKey("game_modes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Host
    status = Column(String, default="pending")
    start_time = Column(DateTime(timezone=True), default=datetime.now(UTC))
    end_time = Column(DateTime(timezone=True), nullable=True)
    first_shot = Column(String, nullable=False)
    first_to = Column(Integer, default=1)

    # 🆕 Wer gerade dran ist
    current_turn_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ---------- Relationships ----------
    user = relationship("User", back_populates="games", foreign_keys=[user_id], lazy="selectin")
    game_mode = relationship("GameMode", back_populates="games", lazy="selectin")
    participants = relationship("GameParticipant", back_populates="game",
                                cascade="all, delete-orphan", lazy="selectin")
    throws = relationship("Throw", back_populates="game",
                          cascade="all, delete-orphan", lazy="selectin")

    # 🆕 Relation zum aktiven Spieler
    current_turn_user = relationship("User", foreign_keys=[current_turn_user_id], lazy="selectin")