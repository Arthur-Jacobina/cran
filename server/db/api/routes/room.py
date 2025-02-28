from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...crud import room as room_crud
from ...app import get_db
from ..schemas.room import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/", response_model=RoomResponse)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    return room_crud.create_room(db, room.dict())

@router.get("/{room_id}", response_model=RoomResponse)
def read_room(room_id: UUID, db: Session = Depends(get_db)):
    db_room = room_crud.get_room(db, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@router.get("/user/{user_id}", response_model=List[RoomResponse])
def read_user_rooms(user_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return room_crud.get_user_rooms(db, user_id, skip=skip, limit=limit)

@router.get("/", response_model=List[RoomResponse])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return room_crud.get_rooms(db, skip=skip, limit=limit)

@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: UUID, room: RoomUpdate, db: Session = Depends(get_db)):
    db_room = room_crud.update_room(db, room_id, room.dict(exclude_unset=True))
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@router.delete("/{room_id}")
def delete_room(room_id: UUID, db: Session = Depends(get_db)):
    success = room_crud.delete_room(db, room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"} 