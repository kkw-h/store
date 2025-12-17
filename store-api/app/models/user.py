from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    """
    用户模型 (User Model)
    存储用户基础信息，支持微信 OpenID 和手机号登录。
    """
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    openid = Column(String(64), nullable=True, unique=True, index=True, comment='微信OpenID (小程序登录用)')
    nickname = Column(String(64), comment='用户昵称')
    avatar_url = Column(String(255), comment='用户头像URL')
    phone = Column(String(20), unique=True, index=True, comment='手机号')
    created_at = Column(DateTime(timezone=True), default=func.now(), comment='注册时间')
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关联关系
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")


class UserAddress(Base):
    """
    用户收货地址模型 (User Address Model)
    """
    __tablename__ = "user_addresses"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment='关联用户ID')
    contact_name = Column(String(64), nullable=False, comment='联系人姓名')
    contact_phone = Column(String(20), nullable=False, comment='联系人电话')
    detail_address = Column(String(255), nullable=False, comment='详细地址 (如: xx路xx小区x号)')
    is_default = Column(Boolean, default=False, comment='是否为默认地址')
    created_at = Column(DateTime(timezone=True), default=func.now(), comment='创建时间')

    # 关联关系
    user = relationship("User", back_populates="addresses")
