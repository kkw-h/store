from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

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
