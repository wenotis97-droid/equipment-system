"""用户管理路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_dep
from app.models.sys_user import SysUser, SysRole, SysDepartment
from app.services.auth_service import create_user
from app.schemas.sys import UserCreate, UserUpdate, RoleOut, DepartmentOut
from app.schemas.common import ResponseBase, PageResult

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(page: int = 1, page_size: int = 20, keyword: str = None,
               db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    q = db.query(SysUser)
    if keyword:
        q = q.filter(SysUser.username.contains(keyword) | SysUser.real_name.contains(keyword))
    total = q.count()
    items = q.order_by(SysUser.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for u in items:
        role = db.query(SysRole).filter(SysRole.id == u.role_id).first()
        result.append({
            "id": u.id,
            "username": u.username,
            "real_name": u.real_name,
            "phone": u.phone,
            "role_id": u.role_id,
            "role_name": role.role_name if role else None,
            "department_id": u.department_id,
            "avatar_url": u.avatar_url,
            "status": u.status,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return ResponseBase.success({"total": total, "page": page, "page_size": page_size, "list": result})


@router.post("")
def create_user_api(req: UserCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    existing = db.query(SysUser).filter(SysUser.username == req.username).first()
    if existing:
        return ResponseBase.error("用户名已存在")
    u = create_user(db, req.username, req.password, req.real_name, req.phone, req.role_id, status=req.status)
    return ResponseBase.success({"id": u.id}, "创建成功")


@router.put("/{user_id}")
def update_user_api(user_id: int, req: UserUpdate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    u = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not u:
        return ResponseBase.error("用户不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(u, k, v)
    db.commit()
    return ResponseBase.success(message="更新成功")


@router.delete("/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    u = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not u:
        return ResponseBase.error("用户不存在")
    if u.id == user.id:
        return ResponseBase.error("不能删除自己")
    db.delete(u)
    db.commit()
    return ResponseBase.success(message="删除成功")


@router.put("/{user_id}/status")
def toggle_status(user_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    u = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not u:
        return ResponseBase.error("用户不存在")
    u.status = 0 if u.status == 1 else 1
    db.commit()
    return ResponseBase.success({"status": u.status})


# 角色
@router.get("/roles/all")
def list_roles(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    roles = db.query(SysRole).all()
    return ResponseBase.success([{
        "id": r.id, "role_name": r.role_name, "role_code": r.role_code,
        "description": r.description, "permissions": r.permissions,
    } for r in roles])


# 部门
@router.get("/departments/all")
def list_departments(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    depts = db.query(SysDepartment).order_by(SysDepartment.sort_order).all()
    return ResponseBase.success([{
        "id": d.id, "dept_name": d.dept_name, "parent_id": d.parent_id,
        "dept_code": d.dept_code, "sort_order": d.sort_order,
    } for d in depts])
