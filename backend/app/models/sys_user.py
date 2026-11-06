"""用户、角色、部门模型"""
from sqlalchemy import Column, String, Integer, Text, JSON, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class SysRole(Base, BaseModel):
    """角色表"""
    __tablename__ = "sys_role"

    role_name = Column(String(64), nullable=False, comment="角色名称")
    role_code = Column(String(64), unique=True, nullable=False, comment="角色编码: admin/manager/operator/driver")
    permissions = Column(JSON, comment="权限列表")
    description = Column(String(255), comment="描述")

    users = relationship("SysUser", back_populates="role")


class SysDepartment(Base, BaseModel):
    """部门表"""
    __tablename__ = "sys_department"

    dept_name = Column(String(128), nullable=False, comment="部门名称")
    parent_id = Column(Integer, default=0, comment="父部门ID")
    dept_code = Column(String(64), comment="部门编码")
    sort_order = Column(Integer, default=0, comment="排序")

    users = relationship("SysUser", back_populates="department")


class SysUser(Base, BaseModel):
    """系统用户表"""
    __tablename__ = "sys_user"

    username = Column(String(64), unique=True, nullable=False, comment="登录名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(64), comment="真实姓名")
    phone = Column(String(20), comment="手机号")
    role_id = Column(Integer, ForeignKey("sys_role.id"), comment="角色ID")
    department_id = Column(Integer, ForeignKey("sys_department.id"), nullable=True, comment="部门ID")
    wx_openid = Column(String(128), comment="微信openid")
    wx_unionid = Column(String(128), comment="微信unionid")
    avatar_url = Column(String(512), comment="头像URL")
    status = Column(Integer, default=1, comment="1启用 0禁用")
    last_login_at = Column(DateTime, comment="最后登录时间")

    role = relationship("SysRole", back_populates="users")
    department = relationship("SysDepartment", back_populates="users")
