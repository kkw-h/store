from typing import Optional, Dict, Any
from pydantic import BaseModel

class OrderAuditRequest(BaseModel):
    order_id: int
    action: str  # 'accept' or 'reject'
    reject_reason: Optional[str] = None

class CompleteDeliveryRequest(BaseModel):
    order_id: int

class VerifyPickupRequest(BaseModel):
    code: str

class VerifyPickupResponse(BaseModel):
    success: bool
    order_info: Dict[str, Any]

class ShopConfigUpdate(BaseModel):
    is_open: int  # 1 for open, 0 for closed
    open_time: str # "HH:MM"
    close_time: str # "HH:MM"
