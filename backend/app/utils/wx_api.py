"""微信 API 调用工具"""
import httpx
from app.config import settings


async def code2session(code: str) -> dict:
    """
    微信小程序 code 换 openid 和 session_key
    文档: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        return resp.json()


async def get_phone_number(phone_code: str) -> str:
    """微信获取手机号（需先获取 access_token）"""
    # 简化实现：实际生产需先获取 access_token 再调用 getuserphonenumber
    # 这里返回占位，实际使用时补充
    return ""
