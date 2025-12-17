from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    """
    订单主表模型 (Order Model)
    存储订单核心状态、金额及配送信息。
    """
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True)
    order_no = Column(String(32), nullable=False, unique=True, comment='业务订单号，如 20231217xxxx')
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment='下单用户ID')
    
    # 金额信息
    total_amount = Column(Numeric(10, 2), nullable=False, comment='商品总价 (未含运费)')
    delivery_fee = Column(Numeric(10, 2), default=0.00, comment='运费')
    final_amount = Column(Numeric(10, 2), nullable=False, comment='实付总金额')
    
    # 订单状态与类型
    # 状态码定义: 
    # 0:待支付, 1:待接单(配送), 2:待自提, 3:配送中, 4:已完成, -1:已取消/退款
    status = Column(Integer, nullable=False, default=0, comment='订单状态')
    delivery_type = Column(String(20), nullable=False, comment='配送方式枚举: delivery(配送) / pickup(自提)')
    
    # 配送信息 (JSONB快照)
    # 结构示例: { "name": "张三", "phone": "138...", "address": "xx路xx号" }
    # 使用快照是为了防止用户修改地址簿后影响历史订单显示
    address_snapshot = Column(JSONB, comment='收货地址快照')
    
    # 自提信息
    pickup_code = Column(String(10), comment='6位自提核销码 (仅自提单有效)')
    pickup_time = Column(DateTime(timezone=True), comment='用户预约的自提时间')
    verified_at = Column(DateTime(timezone=True), comment='核销/完成时间')
    
    # 支付与备注
    transaction_id = Column(String(64), comment='微信支付流水号 (支付回调写入)')
    remark = Column(String(255), comment='用户订单备注')
    reject_reason = Column(String(255), comment='商家拒单原因 (仅拒单时有值)')
    
    created_at = Column(DateTime(timezone=True), default=func.now(), comment='下单时间')
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关联关系
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    timeline = relationship("OrderTimeline", back_populates="order", cascade="all, delete-orphan", order_by="OrderTimeline.created_at")

    # 索引优化
    __table_args__ = (
        Index('idx_orders_user_status', 'user_id', 'status'), # 优化 "我的订单" 列表查询
        Index('idx_orders_pickup_code', 'pickup_code'),       # 优化 "商家扫码核销" 查询
    )


class OrderItem(Base):
    """
    订单明细表模型 (Order Item Model)
    存储订单中包含的商品快照。
    """
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, index=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, index=True, comment='关联订单ID')
    product_id = Column(BigInteger, ForeignKey("products.id"), comment='关联商品ID (商品删除后可能为空，但快照保留)')
    
    # 快照信息 (防止商品改名或改价后历史订单显示错误)
    product_name = Column(String(100), nullable=False, comment='下单时的商品名称快照')
    product_image = Column(String(255), comment='下单时的商品图片快照')
    price = Column(Numeric(10, 2), nullable=False, comment='下单时的商品单价快照')
    quantity = Column(Integer, nullable=False, default=1, comment='购买数量')

    # 关联关系
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class OrderTimeline(Base):
    """
    订单时间轴/操作日志 (Order Timeline)
    记录订单状态流转历史。
    """
    __tablename__ = "order_timeline"

    id = Column(BigInteger, primary_key=True, index=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, index=True, comment='关联订单ID')
    status = Column(String(50), nullable=False, comment='状态/操作描述 (如: 下单成功, 支付成功)')
    remark = Column(String(255), comment='备注信息')
    created_at = Column(DateTime(timezone=True), default=func.now(), comment='发生时间')

    order = relationship("Order", back_populates="timeline")
