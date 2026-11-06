"""FastAPI 应用入口"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, HTMLResponse
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *  # 导入所有模型
from app.routers.admin import admin_router
from app.routers.miniapp import miniapp_router
from app.schemas.common import ResponseBase


# 前端构建产物目录（部署时合并）
FRONTEND_DIST = os.environ.get("FRONTEND_DIST", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist"))


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


@app.get("/", include_in_schema=False)
async def root():
    """根路径：如果有前端构建产物则返回前端页面，否则返回 API 信息"""
    index_html = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {"message": "设备管理系统 API", "docs": "/docs"}


@app.get("/scan", tags=["扫码"])
def scan_redirect(token: str):
    """扫码入口：扫描二维码后重定向到前端设备详情页"""
    # 自适应：部署环境用相对路径，开发环境用 localhost
    base = os.environ.get("QRCODE_BASE_URL", "")
    if base and base != "http://localhost:8000/scan?token=":
        return RedirectResponse(url=f"/#/pages/equipment/detail?token={token}")
    return RedirectResponse(url=f"http://localhost:5174/#/pages/equipment/detail?token={token}")


# 前端路由 fallback（Vue history/hash mode）
@app.get("/{path:path}", include_in_schema=False)
async def frontend_fallback(path: str):
    """非 API、非 uploads 的路径都回退到前端 index.html"""
    # 排除 API 和已挂载的路径
    if path.startswith("api/") or path.startswith("uploads/") or path.startswith("docs") or path.startswith("redoc"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    # 如果请求的是静态资源文件（js/css/img等），尝试从 dist/assets 读取
    file_path = os.path.join(FRONTEND_DIST, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # 否则返回前端 index.html（SPA 路由）
    index_html = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content=ResponseBase.error(f"服务器内部错误: {str(exc)}", 500).model_dump(),
    )
