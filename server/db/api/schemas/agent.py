from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    model: str
    parameters: Optional[dict] = None
    is_active: bool = True

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    model: Optional[str] = None
    is_active: Optional[bool] = None

class AgentResponse(AgentBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # This allows ORM model conversion (previously called orm_mode) 