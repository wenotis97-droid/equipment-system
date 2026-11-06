"""小程序业务路由（加油/运转/报修/培训）"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_miniapp_user
from app.models.sys_user import SysUser
from app.services.fuel_service import create_fuel_record, list_fuel_records
from app.services.operation_service import create_operation_log, get_today_logs
from app.services.repair_service import create_repair, my_repairs
from app.services.training_service import list_training_plans, get_training_plan
from app.schemas.business import FuelRecordCreate, OperationLogCreate, RepairRequestCreate
from app.schemas.common import ResponseBase

# 加油
fuel_router = APIRouter(prefix="/fuel", tags=["小程序加油"])


@fuel_router.post("/records")
def create_fuel(req: FuelRecordCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    req.source = 1  # 小程序扫码
    if not req.operator_name:
        req.operator_name = user.real_name or user.username
    r = create_fuel_record(db, req, user.id)
    return ResponseBase.success({"id": r.id}, "提交成功")


@fuel_router.get("/history")
def fuel_history(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    from app.models.fuel import FuelRecord
    from sqlalchemy import desc
    q = db.query(FuelRecord).filter(FuelRecord.user_id == user.id)
    total = q.count()
    items = q.order_by(desc(FuelRecord.fuel_date)).offset((page - 1) * page_size).limit(page_size).all()
    return ResponseBase.success({"total": total, "page": page, "page_size": page_size, "list": [{
        "id": r.id, "equipment_id": r.equipment_id, "fuel_date": r.fuel_date.isoformat() if r.fuel_date else None,
        "volume": float(r.volume) if r.volume else None, "fuel_type": r.fuel_type,
        "total_amount": float(r.total_amount) if r.total_amount else None,
    } for r in items]})


# 运转
operation_router = APIRouter(prefix="/operation", tags=["小程序运转"])


@operation_router.post("/logs")
def create_operation(req: OperationLogCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    if not req.operator_name:
        req.operator_name = user.real_name or user.username
    try:
        log = create_operation_log(db, req, user.id)
    except ValueError as e:
        return ResponseBase.error(str(e))
    return ResponseBase.success({"id": log.id}, "提交成功")


@operation_router.get("/today")
def today_logs(db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    return ResponseBase.success(get_today_logs(db, user.id))


# 报修
repair_router = APIRouter(prefix="/repair", tags=["小程序报修"])


@repair_router.post("/requests")
def create_repair_api(req: RepairRequestCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    if not req.reporter_name:
        req.reporter_name = user.real_name or user.username
    if not req.reporter_phone:
        req.reporter_phone = user.phone
    r = create_repair(db, req, user.id)
    return ResponseBase.success({"id": r.id, "request_no": r.request_no}, "报修提交成功")


@repair_router.get("/my")
def my_repair_list(db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    return ResponseBase.success(my_repairs(db, user.id))


# 培训
training_router = APIRouter(prefix="/training", tags=["小程序培训"])


@training_router.get("/list")
def training_list(status: int = 1, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    return ResponseBase.success(list_training_plans(db, status, 1, 50))


@training_router.get("/{plan_id}")
def training_detail(plan_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_miniapp_user)):
    p = get_training_plan(db, plan_id)
    if not p:
        return ResponseBase.error("培训不存在")
    return ResponseBase.success(p)
