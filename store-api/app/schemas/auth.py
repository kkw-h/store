from pydantic import BaseModel, Field
from typing import Optional

class WeChatLogin(BaseModel):
    """微信登录请求参数"""
    code: str = Field(..., min_length=1, description="微信临时登录凭证 (jscode)")

class PhoneLogin(BaseModel):
    """手机号登录请求参数"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="短信验证码")

class AdminLogin(BaseModel):
    """管理员登录请求参数"""
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")

class UserInfo(BaseModel):
    """用户信息模型"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=32, description="用户昵称")
    avatar: Optional[str] = Field(None, max_length=512, description="用户头像URL")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号 (部分脱敏)")
    balance: Optional[float] = Field(0.00, ge=0, description="余额")
    points: Optional[int] = Field(0, ge=0, description="积分")

class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=32, description="用户昵称")
    avatar: Optional[str] = Field(None, max_length=512, description="用户头像URL")

class LoginResponse(BaseModel):
    """登录成功响应"""
    token: str = Field(..., description="JWT 访问令牌")
    userInfo: UserInfo = Field(..., description="用户基础信息")
