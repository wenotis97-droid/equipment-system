"""通用 Schema：统一响应、分页"""
from typing import Optional, Any, List, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel):
    """统一响应结构"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None

    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        return cls(code=200, message=message, data=data, timestamp=datetime.now())

    @classmethod
    def error(cls, message: str = "error", code: int = 400, data: Any = None):
        return cls(code=code, message=message, data=data, timestamp=datetime.now())


class PageParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel):
    """分页结果"""
    total: int = 0
    page: int = 1
    page_size: int = 20
    list: List[Any] = []


class IdResult(BaseModel):
    id: int
