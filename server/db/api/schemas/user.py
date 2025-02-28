from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class UserPreferences(BaseModel):
    looks: bool
    personality: bool
    justGirl: bool
    neutral: bool
    techSavvy: bool
    romantic: bool
    animeVibes: bool
    rosie: bool
    cranberry: bool

class UserBase(BaseModel):
    wallet_address: str
    username: str
    twitter_handle: str
    preferences: UserPreferences
    selected_waifus: List[str]

class UserCreate(UserBase):
    wallet_address: str
    username: str
    twitter_handle: str
    preferences: UserPreferences
    selected_waifus: List[str]

class UserUpdate(UserBase):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 