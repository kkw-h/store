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

class LoginResponse(BaseModel):
    """登录成功响应"""
    token: str = Field(..., description="JWT 访问令牌")
    userInfo: UserInfo = Field(..., description="用户基础信息")
