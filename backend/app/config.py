"""应用配置"""
import os
from pydantic_settings import BaseSettings


def _get_cors_origins():
    """自动适配 CORS：开发环境用 localhost，生产环境允许所有"""
    env_origins = os.environ.get("CORS_ORIGINS", "")
    if env_origins:
        return [o.strip() for o in env_origins.split(",") if o.strip()]
    if os.environ.get("RENDER", "") or os.environ.get("PORT", ""):
        # 部署环境，允许所有来源
        return ["*"]
    return ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"]


def _get_qrcode_base_url():
    """二维码扫码跳转基础 URL，自适应环境"""
    env_url = os.environ.get("QRCODE_BASE_URL", "")
    if env_url:
        return env_url
    return "http://localhost:8000/scan?token="


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "设备管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库（默认 SQLite，生产可改为 MySQL）
    DATABASE_URL: str = "sqlite:///./data/equipment.db"

    # JWT
    SECRET_KEY: str = "equipment-system-secret-key-2024-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 文件上传
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    QRCODE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "qrcodes")

    # 二维码访问基础 URL（自动适配环境）
    QRCODE_BASE_URL: str = _get_qrcode_base_url()

    # 微信小程序（生产环境填入真实 AppID 和 Secret）
    WX_APPID: str = "your-miniapp-appid"
    WX_SECRET: str = "your-miniapp-secret"

    # CORS
    CORS_ORIGINS: list = _get_cors_origins()

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 确保目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.QRCODE_DIR, exist_ok=True)
# 确保数据目录存在（SQLite）
db_path = os.path.dirname(os.path.abspath(settings.DATABASE_URL.replace("sqlite:///", "")))
if db_path and db_path != ".":
    os.makedirs(db_path, exist_ok=True)

