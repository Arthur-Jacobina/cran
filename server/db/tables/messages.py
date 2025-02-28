import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    context = Column(JSON, nullable=False)
    role = Column(String, nullable=False)
    status = Column(Boolean, default=False)

    room = relationship("Room", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, room_id={self.room_id}, role={self.role}, status={self.status})>"