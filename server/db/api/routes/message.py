from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...crud import message as message_crud
from ...app import get_db
from ..schemas.message import MessageCreate, MessageUpdate, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageResponse)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    return message_crud.create_message(db, message.dict())

@router.get("/{message_id}", response_model=MessageResponse)
def read_message(message_id: UUID, db: Session = Depends(get_db)):
    db_message = message_crud.get_message(db, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@router.get("/room/{room_id}", response_model=List[MessageResponse])
def read_room_messages(room_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return message_crud.get_room_messages(db, room_id, skip=skip, limit=limit)

@router.put("/{message_id}", response_model=MessageResponse)
def update_message(message_id: UUID, message: MessageUpdate, db: Session = Depends(get_db)):
    db_message = message_crud.update_message(db, message_id, message.dict(exclude_unset=True))
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@router.delete("/{message_id}")
def delete_message(message_id: UUID, db: Session = Depends(get_db)):
    success = message_crud.delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"} 