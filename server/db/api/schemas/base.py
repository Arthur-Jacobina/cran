from pydantic import BaseModel
from uuid import UUID

class BaseResponse(BaseModel):
    id: UUID

    class Config:
        orm_mode = True 