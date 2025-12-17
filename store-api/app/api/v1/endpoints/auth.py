from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core import security
from app.models.user import User
from app.schemas import auth as auth_schemas
from app.schemas.response import ResponseModel, success
from app.services import wechat

router = APIRouter()

@router.post("/login", response_model=ResponseModel[auth_schemas.LoginResponse])
async def login_wechat(
    login_data: auth_schemas.WeChatLogin,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    微信静默登录接口
    
    1. 接收前端传来的 code
    2. 调用微信 API 换取 openid
    3. 根据 openid 查找或创建用户
    4. 颁发 JWT Token
    """
    # 1. 调用微信接口换取 OpenID
    wx_data = await wechat.code_to_session(login_data.code)
    if "errcode" in wx_data and wx_data["errcode"] != 0:
        # 开发环境 Mock 逻辑: 如果是 mock_code 则模拟成功
        if login_data.code == "mock_code":
            openid = "mock_openid_12345"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"WeChat API Error: {wx_data.get('errmsg')}",
            )
    else:
        openid = wx_data.get("openid")
    
    if not openid:
         raise HTTPException(
            status_code=400,
            detail="Failed to retrieve OpenID",
        )

    # 2. 查找用户是否存在
    result = await session.execute(select(User).where(User.openid == openid))
    user = result.scalars().first()

    # 3. 如果不存在则自动注册
    if not user:
        user = User(openid=openid)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # 4. 生成访问令牌 (JWT)
    access_token = security.create_access_token(user.id)
    
    # 返回标准响应
    return success(data={
        "token": access_token,
        "userInfo": {
            "nickname": user.nickname,
            "avatar": user.avatar_url,
            "phone": user.phone
        }
    })

@router.post("/phone", response_model=ResponseModel[auth_schemas.LoginResponse])
async def login_phone(
    login_data: auth_schemas.PhoneLogin,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    手机号登录接口
    
    1. 校验短信验证码 (目前为模拟)
    2. 根据手机号查找或创建用户
    3. 颁发 JWT Token
    """
    # 1. 验证短信验证码 (模拟逻辑: 固定验证码 123456)
    if login_data.code != "123456":
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 2. 查找用户
    result = await session.execute(select(User).where(User.phone == login_data.phone))
    user = result.scalars().first()
    
    # 3. 如果不存在则自动注册
    if not user:
        user = User(phone=login_data.phone)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # 4. 生成 Token
    access_token = security.create_access_token(user.id)
    
    return success(data={
        "token": access_token,
        "userInfo": {
            "nickname": user.nickname,
            "avatar": user.avatar_url,
            "phone": user.phone
        }
    })
