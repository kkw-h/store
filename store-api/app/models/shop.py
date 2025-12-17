from sqlalchemy import Column, Integer, String, Boolean, Numeric, Time, DateTime, func
from app.core.database import Base

class ShopConfig(Base):
    """
    店铺配置模型 (Shop Configuration)
    存储店铺的基础设置、营业状态等，通常只有一行记录。
    """
    __tablename__ = "shop_config"

    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String(100), nullable=False, comment='店铺名称')
    store_address = Column(String(255), comment='店铺物理地址 (自提点)')
    store_phone = Column(String(20), comment='店铺联系电话')
    
    # 营业状态控制
    is_open = Column(Boolean, default=True, comment='总开关: true=营业中, false=打烊')
    open_time = Column(Time, nullable=False, default='09:00:00', comment='每日营业开始时间')
    close_time = Column(Time, nullable=False, default='22:00:00', comment='每日营业结束时间')
    
    # 费用规则
    delivery_fee = Column(Numeric(10, 2), default=0.00, comment='基础运费')
    min_order_amount = Column(Numeric(10, 2), default=0.00, comment='起送金额 (低于此金额不可下单)')
    
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment='最后修改时间')
