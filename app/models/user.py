from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    games = relationship(
        "Game", back_populates="user", cascade="all, delete-orphan",
        foreign_keys="Game.user_id", lazy="selectin"
    )
    statistics = relationship("Statistic", back_populates="user",
                              cascade="all, delete-orphan", lazy="selectin")
    participants = relationship("GameParticipant", back_populates="user",
                                cascade="all, delete-orphan", lazy="selectin")

    friendships_sent = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id1",
        back_populates="user1",
        lazy="selectin"
    )
    friendships_received = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id2",
        back_populates="user2", lazy="selectin"
    )