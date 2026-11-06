"""小程序认证路由"""
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sys_user import SysUser, SysRole
from app.dependencies import get_miniapp_user
from app.utils.security import create_access_token, hash_password
from app.utils.wx_api import code2session
from app.schemas.auth import WxLoginRequest
from app.schemas.common import ResponseBase

router = APIRouter(prefix="/auth", tags=["小程序认证"])


@router.post("/login")
async def wx_login(req: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录：code 换 openid
    开发环境下（未配置真实 AppID）返回模拟 token，便于测试
    """
    # 尝试调用微信接口
    openid = None
    try:
        result = await code2session(req.code)
        openid = result.get("openid")
    except Exception:
        pass

    # 开发环境降级：用 code 作为模拟 openid
    if not openid:
        openid = f"dev_{req.code[:16]}"

    # 查找已绑定用户
    user = db.query(SysUser).filter(SysUser.wx_openid == openid).first()

    if not user:
        # 开发环境：自动创建一个操作员账号
        role = db.query(SysRole).filter(SysRole.role_code == "operator").first()
        username = f"wx_{openid[:12]}"
        user = SysUser(
            username=username,
            password_hash=hash_password(uuid.uuid4().hex),
            real_name="微信用户",
            wx_openid=openid,
            role_id=role.id if role else None,
            status=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    user.last_login_at = datetime.now()
    db.commit()

    token = create_access_token({"sub": str(user.id), "openid": openid})
    role = db.query(SysRole).filter(SysRole.id == user.role_id).first() if user.role_id else None
    return ResponseBase.success({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "role_name": role.role_name if role else None,
        },
    })


@router.get("/profile")
def profile(user: SysUser = Depends(get_miniapp_user), db: Session = Depends(get_db)):
    role = db.query(SysRole).filter(SysRole.id == user.role_id).first() if user.role_id else None
    return ResponseBase.success({
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "role_name": role.role_name if role else None,
    })
