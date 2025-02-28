from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    owner_id: UUID4
    agent_id: Optional[UUID4] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    agent_id: Optional[UUID4] = None

class RoomResponse(RoomBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 