from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text, DateTime, func, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    """
    商品分类模型 (Product Category)
    用于左侧导航栏的分类展示。
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment='分类名称')
    sort_order = Column(Integer, default=0, comment='排序权重，数值越大越靠前')
    is_visible = Column(Boolean, default=True, comment='是否可见 (软删除或隐藏)')

    # 关联关系
    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    商品模型 (Product Model)
    存储商品核心信息。
    """
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), comment='关联分类ID')
    name = Column(String(100), nullable=False, comment='商品名称')
    description = Column(Text, comment='商品详情描述')
    thumb_url = Column(String(255), comment='商品缩略图URL')
    price = Column(Numeric(10, 2), nullable=False, comment='当前售价')
    original_price = Column(Numeric(10, 2), comment='原价/划线价 (展示用)')
    stock = Column(Integer, default=0, nullable=False, comment='库存数量')
    sales_count = Column(Integer, default=0, comment='累计销量 (展示用)')
    status = Column(Integer, default=1, comment='状态: 1=上架, 0=下架')
    specs = Column(JSONB, default=None, comment='预留字段：多规格信息 (JSON格式)')
    created_at = Column(DateTime(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关联关系
    category = relationship("Category", back_populates="products")

    # 索引优化
    __table_args__ = (
        Index('idx_products_cat_status', 'category_id', 'status'), # 优化 "分类下上架商品" 的查询
    )
