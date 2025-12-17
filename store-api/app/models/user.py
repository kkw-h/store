from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    openid = Column(String(64), nullable=False, unique=True, index=True, comment='微信OpenID')
    nickname = Column(String(64))
    avatar_url = Column(String(255))
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    addresses = relationship("UserAddress", back_populates="user")
    orders = relationship("Order", back_populates="user")


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    contact_name = Column(String(64), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    detail_address = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship("User", back_populates="addresses")
