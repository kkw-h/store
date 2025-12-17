from pydantic import BaseModel, Field
from typing import Optional

class WeChatLogin(BaseModel):
    """微信登录请求参数"""
    code: str = Field(..., description="微信临时登录凭证 (jscode)")

class PhoneLogin(BaseModel):
    """手机号登录请求参数"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="短信验证码")

class UserInfo(BaseModel):
    """用户信息模型"""
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar: Optional[str] = Field(None, description="用户头像URL")
    phone: Optional[str] = Field(None, description="手机号 (部分脱敏)")
    balance: Optional[float] = Field(0.00, description="余额")
    points: Optional[int] = Field(0, description="积分")

class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None

class LoginResponse(BaseModel):
    """登录成功响应"""
    token: str = Field(..., description="JWT 访问令牌")
    userInfo: UserInfo = Field(..., description="用户基础信息")
