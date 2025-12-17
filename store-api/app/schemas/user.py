from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    openid: Optional[str] = None

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    openid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
