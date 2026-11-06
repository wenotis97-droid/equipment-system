"""认证服务"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.sys_user import SysUser, SysRole
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from app.schemas.auth import LoginRequest, UserInfo
from app.config import settings


def authenticate(db: Session, req: LoginRequest) -> dict | None:
    """账号密码登录，返回 token + 用户信息"""
    user = db.query(SysUser).filter(SysUser.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        return None
    if user.status != 1:
        return None

    user.last_login_at = datetime.now()
    db.commit()

    token = create_access_token({"sub": str(user.id), "username": user.username})
    role = db.query(SysRole).filter(SysRole.id == user.role_id).first() if user.role_id else None
    info = UserInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        phone=user.phone,
        role_id=user.role_id,
        role_name=role.role_name if role else None,
        role_code=role.role_code if role else None,
        department_id=user.department_id,
        avatar_url=user.avatar_url,
        permissions=role.permissions if role else [],
    )
    return {"access_token": token, "token_type": "bearer", "user": info}


def get_current_user(db: Session, token: str) -> SysUser | None:
    """从 token 解析当前用户"""
    payload = decode_access_token(token.replace("Bearer ", ""))
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(SysUser).filter(SysUser.id == int(user_id)).first()


def create_user(db: Session, username: str, password: str, real_name: str = None, phone: str = None, role_id: int = None, status: int = 1):
    """创建用户"""
    user = SysUser(
        username=username,
        password_hash=hash_password(password),
        real_name=real_name,
        phone=phone,
        role_id=role_id,
        status=status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
