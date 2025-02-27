import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=True)

    messages = relationship("Message", back_populates="room", cascade="all, delete")

    user = relationship("User", back_populates="rooms")

    def __repr__(self):
        return f"<Room(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id})>"
