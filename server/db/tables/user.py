from sqlalchemy import Column, String, JSON, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_address = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    twitter_handle = Column(String, unique=True, index=True, nullable=False)
    preferences = Column(JSON, nullable=False)
    selected_waifus = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    rooms = relationship("Room", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, wallet_address={self.wallet_address})>"