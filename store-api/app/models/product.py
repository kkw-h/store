from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text, DateTime, func, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0, comment='排序权重，越大越前')
    is_visible = Column(Boolean, default=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    thumb_url = Column(String(255), comment='商品缩略图')
    price = Column(Numeric(10, 2), nullable=False, comment='当前售价')
    original_price = Column(Numeric(10, 2), comment='原价/划线价')
    stock = Column(Integer, default=0, nullable=False, comment='库存')
    sales_count = Column(Integer, default=0, comment='销量(展示用)')
    status = Column(Integer, default=1, comment='1:上架 0:下架')
    specs = Column(JSONB, default=None, comment='预留字段：多规格信息')
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")

    __table_args__ = (
        Index('idx_products_cat_status', 'category_id', 'status'),
    )
