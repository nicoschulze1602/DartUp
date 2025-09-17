from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id1 = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id2 = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user1 = relationship("User", foreign_keys=[user_id1], back_populates="friendships_sent")
    user2 = relationship("User", foreign_keys=[user_id2], back_populates="friendships_received")