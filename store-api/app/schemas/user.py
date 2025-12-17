from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    nickname: Optional[str] = Field(None, min_length=1, max_length=32, description="用户昵称")
    avatar_url: Optional[str] = Field(None, max_length=512, description="用户头像URL")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")

class UserCreate(UserBase):
    openid: Optional[str] = Field(None, description="微信OpenID")

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    openid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
