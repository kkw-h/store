from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

class CartAdd(BaseModel):
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(1, gt=0, le=99, description="数量")

class CartUpdate(BaseModel):
    id: int = Field(..., gt=0, description="购物车项ID")
    quantity: Optional[int] = Field(None, gt=0, le=99, description="数量")
    selected: Optional[bool] = Field(None, description="是否选中")

class CartDelete(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="要删除的购物车项ID列表")

class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    price: Decimal
    quantity: int
    selected: bool
    stock: int # Useful for frontend to show if out of stock

    
    model_config = ConfigDict(from_attributes=True)

class CartListOut(BaseModel):
    list: List[CartItemOut]
    total_amount: Decimal # Selected items total amount
    selected_count: int
