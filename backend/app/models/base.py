"""模型基类"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime


class BaseModel:
    """所有模型的混入基类，包含 id、created_at、updated_at
    使用 Integer 而非 BigInteger，保证 SQLite 兼容（生产 MySQL 同样支持）"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
