from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship  # Add this import
from .base import Base  # Import the base class

class User(Base):
    __tablename__ = "users"

    wallet_address = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    room_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # Array of UUIDs

    rooms = relationship("Room", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User(wallet_address={self.wallet_address}, username={self.username})>"