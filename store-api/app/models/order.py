from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True)
    order_no = Column(String(32), nullable=False, unique=True, comment='业务订单号，如 20231217xxxx')
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # 金额信息
    total_amount = Column(Numeric(10, 2), nullable=False, comment='商品总价')
    delivery_fee = Column(Numeric(10, 2), default=0.00, comment='运费')
    final_amount = Column(Numeric(10, 2), nullable=False, comment='实付金额')
    
    # 订单状态与类型
    # 状态码: 0:待支付, 1:待接单(配送), 2:待自提, 3:配送中, 4:已完成, -1:已取消/退款
    status = Column(Integer, nullable=False, default=0)
    delivery_type = Column(String(20), nullable=False, comment='枚举: delivery / pickup')
    
    # 配送信息 (JSONB快照)
    # 结构: { "name": "张三", "phone": "138...", "address": "xx路xx号" }
    address_snapshot = Column(JSONB)
    
    # 自提信息
    pickup_code = Column(String(10), comment='6位核销码')
    pickup_time = Column(DateTime(timezone=True), comment='预约自提时间')
    verified_at = Column(DateTime(timezone=True), comment='核销/完成时间')
    
    # 支付与备注
    transaction_id = Column(String(64), comment='微信支付流水号')
    remark = Column(String(255), comment='用户备注')
    reject_reason = Column(String(255), comment='商家拒单原因')
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    __table_args__ = (
        Index('idx_orders_user_status', 'user_id', 'status'),
        Index('idx_orders_pickup_code', 'pickup_code'),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, index=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
    
    # 快照信息 (防止商品改名或改价后历史订单显示错误)
    product_name = Column(String(100), nullable=False)
    product_image = Column(String(255))
    price = Column(Numeric(10, 2), nullable=False, comment='购买时的单价')
    quantity = Column(Integer, nullable=False, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
