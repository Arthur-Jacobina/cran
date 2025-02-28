import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="rooms")
    agent = relationship("Agent", back_populates="rooms")
    messages = relationship("Message", back_populates="room", cascade="all, delete")

    def __repr__(self):
        return f"<Room(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id})>"