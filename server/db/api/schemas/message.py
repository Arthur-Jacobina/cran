from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    room_id: UUID4
    user_id: Optional[UUID4] = None
    agent_id: Optional[UUID4] = None
    parent_id: Optional[UUID4] = None

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None

class MessageResponse(MessageBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 