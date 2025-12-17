from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

# --- Category Schemas ---

class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., max_length=50, description="分类名称")
    sort_order: int = Field(0, description="排序权重")
    is_visible: bool = Field(True, description="是否可见")

class CategoryCreate(CategoryBase):
    """创建分类"""
    pass

class CategoryUpdate(CategoryBase):
    """更新分类"""
    name: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_visible: Optional[bool] = None

class CategoryOut(CategoryBase):
    """分类响应"""
    id: int

    class Config:
        from_attributes = True

# --- Product Schemas ---

class ProductBase(BaseModel):
    """商品基础模型"""
    category_id: int = Field(..., description="所属分类ID")
    name: str = Field(..., max_length=100, description="商品名称")
    description: Optional[str] = Field(None, description="详情描述")
    thumb_url: Optional[str] = Field(None, max_length=255, description="缩略图URL")
    price: Decimal = Field(..., max_digits=10, decimal_places=2, description="当前售价")
    original_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2, description="原价")
    stock: int = Field(0, ge=0, description="库存")
    status: int = Field(1, description="状态: 1上架 0下架")
    specs: Optional[dict] = Field(None, description="多规格信息 (JSON)")

class ProductCreate(ProductBase):
    """创建商品"""
    pass

class ProductUpdate(BaseModel):
    """更新商品"""
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    thumb_url: Optional[str] = Field(None, max_length=255)
    price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    original_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)
    status: Optional[int] = None
    specs: Optional[dict] = None

class ProductOut(ProductBase):
    """商品响应"""
    id: int
    sales_count: int

    class Config:
        from_attributes = True

class ProductListOut(BaseModel):
    """商品列表响应 (带分页)"""
    list: List[ProductOut]
    total: int
    page: int
    size: int
