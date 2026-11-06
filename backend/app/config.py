"""应用配置"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "设备管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库（默认 SQLite，生产可改为 MySQL）
    DATABASE_URL: str = "sqlite:///./equipment.db"

    # JWT
    SECRET_KEY: str = "equipment-system-secret-key-2024-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 文件上传
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    QRCODE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "qrcodes")

    # 二维码访问基础 URL（生产环境替换为正式域名）
    QRCODE_BASE_URL: str = "http://localhost:8000/scan?token="

    # 微信小程序（生产环境填入真实 AppID 和 Secret）
    WX_APPID: str = "your-miniapp-appid"
    WX_SECRET: str = "your-miniapp-secret"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 确保目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.QRCODE_DIR, exist_ok=True)
