import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from .base import Base  # Import the base class

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    agent_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # Array of UUIDs
    room_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # Array of UUIDs

    rooms = relationship("Room", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
