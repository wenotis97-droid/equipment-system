"""小程序路由汇总"""
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_miniapp_user
from app.models.sys_user import SysUser
from app.utils.file_upload import save_upload_file
from app.schemas.common import ResponseBase
from app.routers.miniapp.auth import router as auth_router
from app.routers.miniapp.equipment import router as equipment_router
from app.routers.miniapp.business import (
    fuel_router, operation_router, repair_router, training_router,
)

miniapp_router = APIRouter(prefix="/miniapp")
miniapp_router.include_router(auth_router)
miniapp_router.include_router(equipment_router)
miniapp_router.include_router(fuel_router)
miniapp_router.include_router(operation_router)
miniapp_router.include_router(repair_router)
miniapp_router.include_router(training_router)


# 文件上传
@miniapp_router.post("/upload", tags=["小程序文件上传"])
async def upload_file(file: UploadFile = File(...), user: SysUser = Depends(get_miniapp_user)):
    url = await save_upload_file(file, "miniapp")
    return ResponseBase.success({"url": url})
