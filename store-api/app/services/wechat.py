import httpx
from app.core.config import settings

async def code_to_session(code: str) -> dict:
    """
    微信小程序登录凭证校验 (jscode2session)
    
    Args:
        code: 小程序端通过 wx.login 获取的 code
        
    Returns:
        dict: 微信 API 返回的 JSON 数据
        - openid: 用户唯一标识
        - session_key: 会话密钥
        - errcode: 错误码 (0表示成功)
        - errmsg: 错误信息
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
