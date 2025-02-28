from uuid import UUID
from sqlalchemy.orm import Session
from ..tables.room import Room
from typing import Optional, List, Dict, Any

def create_room(db: Session, room_data: Dict[str, Any]) -> Room:
    """Create a new room"""
    db_room = Room(**room_data)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_room(db: Session, room_id: UUID) -> Optional[Room]:
    """Get a room by ID"""
    return db.query(Room).filter(Room.id == room_id).first()

def get_user_rooms(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Room]:
    """Get all rooms for a specific user"""
    return db.query(Room).filter(Room.user_id == user_id).offset(skip).limit(limit).all()

def get_rooms(db: Session, skip: int = 0, limit: int = 100) -> List[Room]:
    """Get all rooms with pagination"""
    return db.query(Room).offset(skip).limit(limit).all()

def update_room(db: Session, room_id: UUID, room_data: Dict[str, Any]) -> Optional[Room]:
    """Update a room"""
    db_room = get_room(db, room_id)
    if db_room:
        for key, value in room_data.items():
            setattr(db_room, key, value)
        db.commit()
        db.refresh(db_room)
    return db_room

def delete_room(db: Session, room_id: UUID) -> bool:
    """Delete a room"""
    db_room = get_room(db, room_id)
    if db_room:
        db.delete(db_room)
        db.commit()
        return True
    return False 