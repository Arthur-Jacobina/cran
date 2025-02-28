# TBD: UserDB with userinfo (related to memory)\

from .tables.base import SessionLocal

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
