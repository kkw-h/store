from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal

class CartAdd(BaseModel):
    product_id: int
    quantity: int = Field(1, gt=0, description="数量")

class CartUpdate(BaseModel):
    id: int
    quantity: Optional[int] = Field(None, gt=0, description="数量")
    selected: Optional[bool] = None

class CartDelete(BaseModel):
    ids: List[int] = Field(..., description="要删除的购物车项ID列表")

class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    price: Decimal
    quantity: int
    selected: bool
    stock: int # Useful for frontend to show if out of stock

    class Config:
        from_attributes = True

class CartListOut(BaseModel):
    list: List[CartItemOut]
    total_amount: Decimal # Selected items total amount
    selected_count: int
