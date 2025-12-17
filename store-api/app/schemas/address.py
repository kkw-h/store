from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AddressBase(BaseModel):
    """
    地址基础模型 (包含创建和更新共用的字段)
    """
    contact_name: str = Field(..., max_length=64, description="联系人姓名")
    contact_phone: str = Field(..., max_length=20, description="联系人电话")
    detail_address: str = Field(..., max_length=255, description="详细地址")
    is_default: bool = Field(False, description="是否设为默认地址")

class AddressCreate(AddressBase):
    """创建地址请求模型"""
    pass

class AddressUpdate(BaseModel):
    """更新地址请求模型 (所有字段可选)"""
    contact_name: Optional[str] = Field(None, max_length=64, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系人电话")
    detail_address: Optional[str] = Field(None, max_length=255, description="详细地址")
    is_default: Optional[bool] = Field(None, description="是否设为默认地址")

class AddressOut(AddressBase):
    """地址信息响应模型"""
    id: int = Field(..., description="地址ID")
    user_id: int = Field(..., description="所属用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
