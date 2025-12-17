from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List
from decimal import Decimal
from app.services.storage import storage

# --- Category Schemas ---

class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    sort_order: int = Field(0, ge=0, description="排序权重")
    is_visible: bool = Field(True, description="是否可见")

class CategoryCreate(CategoryBase):
    """创建分类"""
    pass

class CategoryUpdate(CategoryBase):
    """更新分类"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    sort_order: Optional[int] = Field(None, ge=0, description="排序权重")
    is_visible: Optional[bool] = Field(None, description="是否可见")

class CategoryOut(CategoryBase):
    """分类响应"""
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Product Schemas ---

class ProductBase(BaseModel):
    """商品基础模型"""
    category_id: int = Field(..., gt=0, description="所属分类ID")
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    description: Optional[str] = Field(None, description="详情描述")
    thumb_url: Optional[str] = Field(None, max_length=255, description="缩略图URL")
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="当前售价")
    original_price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="原价")
    stock: int = Field(0, ge=0, description="库存")
    status: int = Field(1, ge=0, le=1, description="状态: 1上架 0下架")
    specs: Optional[dict] = Field(None, description="多规格信息 (JSON)")

class ProductCreate(ProductBase):
    """创建商品"""
    pass

class ProductUpdate(BaseModel):
    """更新商品"""
    category_id: Optional[int] = Field(None, gt=0, description="所属分类ID")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="商品名称")
    description: Optional[str] = Field(None, description="详情描述")
    thumb_url: Optional[str] = Field(None, max_length=255, description="缩略图URL")
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="当前售价")
    original_price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="原价")
    stock: Optional[int] = Field(None, ge=0, description="库存")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态: 1上架 0下架")
    specs: Optional[dict] = Field(None, description="多规格信息 (JSON)")

class ProductOut(ProductBase):
    """商品响应"""
    id: int
    sales_count: int
    thumb_path: Optional[str] = Field(None, description="图片存储路径")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def compute_urls(self):
        # 如果有 thumb_url (此时是数据库中的 path)，则保存到 thumb_path 并转换为 url
        if self.thumb_url:
            self.thumb_path = self.thumb_url
            if not self.thumb_url.startswith('http'):
                self.thumb_url = storage.get_file_url(self.thumb_url)
        return self

class ProductListOut(BaseModel):
    """商品列表响应 (带分页)"""
    list: List[ProductOut]
    total: int
    page: int
    size: int
