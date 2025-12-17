from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class OrderAuditRequest(BaseModel):
    order_id: int = Field(..., gt=0, description="订单ID")
    action: Literal['accept', 'reject'] = Field(..., description="操作类型: accept-接单, reject-拒绝")
    reject_reason: Optional[str] = Field(None, max_length=255, description="拒绝原因")

class CompleteDeliveryRequest(BaseModel):
    order_id: int = Field(..., gt=0, description="订单ID")

class VerifyPickupRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=20, description="核销码")

class VerifyPickupResponse(BaseModel):
    success: bool
    order_info: Dict[str, Any]

class ShopConfigUpdate(BaseModel):
    is_open: int = Field(..., ge=0, le=1, description="营业状态: 1-营业中, 0-休息中")
    open_time: str = Field(..., pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="营业开始时间 (HH:MM)")
    close_time: str = Field(..., pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="营业结束时间 (HH:MM)")
    delivery_fee: float = Field(..., ge=0, description="基础运费")
    min_order_amount: float = Field(..., ge=0, description="起送金额")
    store_name: str = Field(..., min_length=1, max_length=50, description="店铺名称")
    store_address: Optional[str] = Field(None, max_length=255, description="店铺地址")
    store_phone: Optional[str] = Field(None, max_length=20, description="联系电话")

class ShopConfigOut(BaseModel):
    is_open: bool
    open_time: str
    close_time: str
    delivery_fee: float
    min_order_amount: float
    store_name: str
    store_address: Optional[str] = None
    store_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
