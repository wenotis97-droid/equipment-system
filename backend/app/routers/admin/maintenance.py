"""维保管理路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_dep
from app.models.sys_user import SysUser
from app.services.maintenance_service import (
    list_plans, create_plan, update_plan, delete_plan,
    list_records, create_record,
    list_reminders, action_reminder,
)
from app.schemas.business import MaintenancePlanCreate, MaintenanceRecordCreate, ReminderActionRequest
from app.schemas.common import ResponseBase

router = APIRouter(prefix="/maintenance", tags=["维保管理"])


# 维保计划
@router.get("/plans")
def list_plans_api(equipment_id: int = None, page: int = 1, page_size: int = 20,
                   db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_plans(db, equipment_id, page, page_size))


@router.post("/plans")
def create_plan_api(req: MaintenancePlanCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    p = create_plan(db, req)
    return ResponseBase.success({"id": p.id}, "创建成功")


@router.put("/plans/{plan_id}")
def update_plan_api(plan_id: int, data: dict, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    p = update_plan(db, plan_id, data)
    if not p:
        return ResponseBase.error("计划不存在")
    return ResponseBase.success(message="更新成功")


@router.delete("/plans/{plan_id}")
def delete_plan_api(plan_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    if not delete_plan(db, plan_id):
        return ResponseBase.error("计划不存在")
    return ResponseBase.success(message="删除成功")


# 维保记录
@router.get("/records")
def list_records_api(equipment_id: int = None, page: int = 1, page_size: int = 20,
                     db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_records(db, equipment_id, page, page_size))


@router.post("/records")
def create_record_api(req: MaintenanceRecordCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    r = create_record(db, req, user.id)
    return ResponseBase.success({"id": r.id}, "添加成功")


# 维保提醒
@router.get("/reminders")
def list_reminders_api(status: int = None, page: int = 1, page_size: int = 20,
                       db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_reminders(db, status, page, page_size))


@router.put("/reminders/{reminder_id}")
def action_reminder_api(reminder_id: int, req: ReminderActionRequest,
                        db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    if not action_reminder(db, reminder_id, req.action):
        return ResponseBase.error("提醒不存在")
    return ResponseBase.success(message="已处理")
