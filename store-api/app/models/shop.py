from sqlalchemy import Column, Integer, String, Boolean, Numeric, Time, DateTime, func
from app.core.database import Base

class ShopConfig(Base):
    __tablename__ = "shop_config"

    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String(100), nullable=False)
    store_address = Column(String(255))
    store_phone = Column(String(20))
    is_open = Column(Boolean, default=True, comment='总开关: true营业 false打烊')
    open_time = Column(Time, nullable=False, default='09:00:00')
    close_time = Column(Time, nullable=False, default='22:00:00')
    delivery_fee = Column(Numeric(10, 2), default=0.00, comment='基础运费')
    min_order_amount = Column(Numeric(10, 2), default=0.00, comment='起送金额')
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
