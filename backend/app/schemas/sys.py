"""用户管理 Schema"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[int] = 1


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[int] = None


class UserOut(BaseModel):
    id: int
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    department_id: Optional[int] = None
    avatar_url: Optional[str] = None
    status: Optional[int] = 1
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: int
    role_name: str
    role_code: str
    description: Optional[str] = None
    permissions: Optional[list] = None

    class Config:
        from_attributes = True


class DepartmentOut(BaseModel):
    id: int
    dept_name: str
    parent_id: Optional[int] = 0
    dept_code: Optional[str] = None
    sort_order: Optional[int] = 0

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    project_name: str
    project_code: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[int] = 1
    manager_name: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    content: Optional[str] = None
    type: Optional[str] = None
    ref_type: Optional[str] = None
    ref_id: Optional[int] = None
    is_read: Optional[int] = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
