"""FastAPI 应用入口"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *  # 导入所有模型
from app.routers.admin import admin_router
from app.routers.miniapp import miniapp_router
from app.schemas.common import ResponseBase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时建表 + 初始化定时任务"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 初始化定时任务
    from app.scheduler import init_scheduler
    init_scheduler()
    print("[启动] 定时任务已初始化")

    # 初始化示例数据（首次启动）
    from app.init_data import init_data
    db = SessionLocal()
    try:
        init_data(db)
    finally:
        db.close()

    yield

    # 关闭
    from app.scheduler import scheduler
    scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="施工企业设备管理系统 - 后台管理 + 微信小程序互联",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（上传的文件、二维码）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 路由
app.include_router(admin_router, prefix="/api")
app.include_router(miniapp_router, prefix="/api")


@app.get("/", tags=["默认"])
def root():
    return {"message": "设备管理系统 API", "docs": "/docs"}


@app.get("/scan", tags=["扫码"])
def scan_redirect(token: str):
    """扫码入口：扫描二维码后重定向到小程序页面
    生产环境应配置为微信小程序的扫普通链接二维码打开小程序规则
    开发环境重定向到 H5 预览页
    """
    # 重定向到小程序 H5 版本的扫码结果页
    return RedirectResponse(url=f"http://localhost:5174/#/pages/equipment/detail?token={token}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content=ResponseBase.error(f"服务器内部错误: {str(exc)}", 500).model_dump(),
    )
