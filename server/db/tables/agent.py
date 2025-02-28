import uuid
from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Agent(Base):
    __tablename__ = "agent"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    personality = Column(JSON, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    voicepreset = Column(String)

    # Add relationship to rooms
    rooms = relationship("Room", backref="agent")

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name})>"