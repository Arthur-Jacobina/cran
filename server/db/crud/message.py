from uuid import UUID
from sqlalchemy.orm import Session
from ..tables.messages import Message
from typing import Optional, List, Dict, Any

def create_message(db: Session, message_data: Dict[str, Any]) -> Message:
    """Create a new message"""
    db_message = Message(**message_data)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message(db: Session, message_id: UUID) -> Optional[Message]:
    """Get a message by ID"""
    return db.query(Message).filter(Message.id == message_id).first()

def get_room_messages(db: Session, room_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
    """Get all messages for a specific room"""
    return db.query(Message).filter(Message.room_id == room_id).offset(skip).limit(limit).all()

def get_messages(db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
    """Get all messages with pagination"""
    return db.query(Message).offset(skip).limit(limit).all()

def update_message(db: Session, message_id: UUID, message_data: Dict[str, Any]) -> Optional[Message]:
    """Update a message"""
    db_message = get_message(db, message_id)
    if db_message:
        for key, value in message_data.items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: UUID) -> bool:
    """Delete a message"""
    db_message = get_message(db, message_id)
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False 