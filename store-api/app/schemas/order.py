from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

class DeliveryType(str, Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"

class OrderStatus(int, Enum):
    PENDING_PAYMENT = 0
    PENDING_DELIVERY = 1
    PENDING_PICKUP = 2
    DELIVERING = 3
    COMPLETED = 4
    CANCELLED = -1

class OrderItemBase(BaseModel):
    product_id: int
    count: int = Field(..., gt=0, description="购买数量")

# --- Preview Schemas ---

class OrderPreviewRequest(BaseModel):
    items: List[OrderItemBase]
    delivery_type: DeliveryType

class OrderPreviewResponse(BaseModel):
    total_goods_price: Decimal
    delivery_fee: Decimal
    final_price: Decimal
    is_open: bool
    delivery_msg: str

# --- Create Schemas ---

class OrderCreateRequest(BaseModel):
    items: List[OrderItemBase]
    delivery_type: DeliveryType
    remark: Optional[str] = Field(None, max_length=255)
    
    # Pickup specific
    pickup_time: Optional[datetime] = None
    user_phone: Optional[str] = None
    
    # Delivery specific
    address_id: Optional[int] = None

class OrderCreateResponse(BaseModel):
    order_id: int
    order_no: str
    pay_params: dict # Mocked for now

# --- List & Detail Schemas ---

class OrderItemOut(BaseModel):
    product_id: Optional[int]
    product_name: str
    product_image: Optional[str]
    price: Decimal
    quantity: int
    
    class Config:
        from_attributes = True

class OrderTimelineOut(BaseModel):
    status: str
    created_at: datetime = Field(..., alias="time") # Map created_at to time in response

    @field_validator('created_at', mode='after')
    def format_time(cls, v: datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    class Config:
        from_attributes = True
        populate_by_name = True

class OrderListOut(BaseModel):
    id: int
    order_no: str
    status: int
    status_text: str # Computed field
    final_amount: Decimal
    created_at: datetime
    items: List[OrderItemOut]
    
    # User info for admin
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class OrderDetailOut(OrderListOut):
    delivery_type: str
    delivery_fee: Decimal
    total_amount: Decimal
    remark: Optional[str]
    pickup_code: Optional[str] = None
    qrcode_url: Optional[str] = None
    timeline: List[OrderTimelineOut] = Field(default_factory=list, alias="timeline") # Use real timeline model
    address_snapshot: Optional[Any] = None

class OrderCancelRequest(BaseModel):
    order_id: int
    reason: Optional[str] = None
