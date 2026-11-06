"""后台认证路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_dep
from app.models.sys_user import SysUser
from app.services.auth_service import authenticate
from app.schemas.auth import LoginRequest, ChangePasswordRequest, UserInfo
from app.schemas.common import ResponseBase
from app.utils.security import hash_password, verify_password
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["后台认证"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    result = authenticate(db, req)
    if not result:
        return ResponseBase.error("用户名或密码错误", 401)
    return ResponseBase.success(result)


@router.get("/profile")
def profile(user: SysUser = Depends(get_current_user_dep), db: Session = Depends(get_db)):
    from app.models.sys_user import SysRole
    role = db.query(SysRole).filter(SysRole.id == user.role_id).first() if user.role_id else None
    return ResponseBase.success({
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "role_id": user.role_id,
        "role_name": role.role_name if role else None,
        "role_code": role.role_code if role else None,
        "department_id": user.department_id,
        "avatar_url": user.avatar_url,
        "permissions": role.permissions if role else [],
    })


@router.put("/password")
def change_password(req: ChangePasswordRequest,
                   user: SysUser = Depends(get_current_user_dep),
                   db: Session = Depends(get_db)):
    if not verify_password(req.old_password, user.password_hash):
        return ResponseBase.error("原密码错误")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    return ResponseBase.success(message="密码修改成功")
