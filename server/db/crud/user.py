from sqlalchemy.orm import Session
from ..tables.user import User
from typing import Optional, List, Dict, Any

def create_user(db: Session, wallet_address: str, username: str) -> User:
    """Create a new user"""
    db_user = User(wallet_address=wallet_address, username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, wallet_address: str) -> Optional[User]:
    """Get a user by wallet address"""
    return db.query(User).filter(User.wallet_address == wallet_address).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, wallet_address: str, user_data: Dict[str, Any]) -> Optional[User]:
    """Update a user"""
    db_user = get_user(db, wallet_address)
    if db_user:
        for key, value in user_data.items():
            if hasattr(db_user, key):  # Only update existing attributes
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, wallet_address: str) -> bool:
    """Delete a user"""
    db_user = get_user(db, wallet_address)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False 