"""小程序设备路由（扫码识别）"""
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_optional_miniapp_user, get_miniapp_user
from app.models.sys_user import SysUser
from app.models.misc import QrCodeLog
from app.services.equipment_service import get_equipment_by_qr, get_equipment_detail
from app.schemas.common import ResponseBase

router = APIRouter(prefix="/equipment", tags=["小程序设备"])


@router.get("/by-qr/{qr_token}")
def scan_equipment(qr_token: str, request: Request,
                   db: Session = Depends(get_db),
                   user: SysUser = Depends(get_optional_miniapp_user)):
    """扫码识别设备——查看信息可免登录"""
    eq = get_equipment_by_qr(db, qr_token)
    if not eq:
        return ResponseBase.error("二维码无效，设备未找到", 404)

    # 记录扫码日志
    log = QrCodeLog(
        equipment_id=eq.id,
        qr_token=qr_token,
        user_id=user.id if user else None,
        wx_openid=user.wx_openid if user else None,
        scan_time=datetime.now(),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", ""),
    )
    db.add(log)
    db.commit()

    detail = get_equipment_detail(db, eq.id)
    return ResponseBase.success(detail)


@router.get("/{equipment_id}")
def get_equipment(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    detail = get_equipment_detail(db, equipment_id)
    if not detail:
        return ResponseBase.error("设备不存在")
    return ResponseBase.success(detail)
