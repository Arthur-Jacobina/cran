import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Agent(Base):
    __tablename__ = "agent"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid64)
    name = Column(String, nullable=False)
    personality - Column(JSON, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    voicepreset = Column(String)