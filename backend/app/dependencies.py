"""公共依赖"""
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sys_user import SysUser
from app.services.auth_service import get_current_user


def get_current_user_dep(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> SysUser:
    """后台管理端：从 Authorization Header 解析当前用户"""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证Token")
    user = get_current_user(db, authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效或已过期")
    if user.status != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")
    return user


def get_miniapp_user(
    x_session_token: str = Header(None, alias="X-Session-Token"),
    db: Session = Depends(get_db),
) -> SysUser:
    """小程序端：从 X-Session-Token Header 解析当前用户"""
    if not x_session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    # 小程序也用 JWT，token 直接是 session_token
    user = get_current_user(db, f"Bearer {x_session_token}")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期，请重新登录")
    return user


def get_optional_miniapp_user(
    x_session_token: str = Header(None, alias="X-Session-Token"),
    db: Session = Depends(get_db),
) -> SysUser | None:
    """小程序端：可选的当前用户（查看设备信息可免登录）"""
    if not x_session_token:
        return None
    return get_current_user(db, f"Bearer {x_session_token}")
