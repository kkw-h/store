from sqlalchemy import Column, Integer, Boolean, DateTime, func, BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class CartItem(Base):
    """
    购物车项模型 (Cart Item Model)
    存储用户购物车中的商品信息。
    """
    __tablename__ = "cart_items"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment='关联用户ID')
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, comment='关联商品ID')
    quantity = Column(Integer, default=1, nullable=False, comment='购买数量')
    selected = Column(Boolean, default=True, comment='是否选中 (结算用)')
    created_at = Column(DateTime(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关联关系
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")

    # 联合唯一索引，确保同一个用户同一个商品只有一条记录
    __table_args__ = (
        Index('idx_cart_user_product', 'user_id', 'product_id', unique=True),
    )
