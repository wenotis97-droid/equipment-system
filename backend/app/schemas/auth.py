"""认证相关 Schema"""
from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional["UserInfo"] = None


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    role_code: Optional[str] = None
    department_id: Optional[int] = None
    avatar_url: Optional[str] = None
    permissions: Optional[list] = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class WxLoginRequest(BaseModel):
    code: str


class WxBindPhoneRequest(BaseModel):
    phone_code: str


TokenResponse.model_rebuild()
