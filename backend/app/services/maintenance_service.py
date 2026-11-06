"""维保服务 + 自动提醒逻辑"""
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.equipment import Equipment
from app.models.maintenance import MaintenancePlan, MaintenanceRecord, MaintenanceReminder
from app.models.misc import Notification
from app.schemas.business import MaintenancePlanCreate, MaintenanceRecordCreate
import json


def list_plans(db: Session, equipment_id: int = None, page: int = 1, page_size: int = 20) -> dict:
    q = db.query(MaintenancePlan)
    if equipment_id:
        q = q.filter(MaintenancePlan.equipment_id == equipment_id)
    total = q.count()
    items = q.order_by(MaintenancePlan.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "list": [_plan_to_dict(db, p) for p in items]}


def _plan_to_dict(db: Session, p: MaintenancePlan) -> dict:
    eq = db.query(Equipment).filter(Equipment.id == p.equipment_id).first()
    return {
        "id": p.id,
        "equipment_id": p.equipment_id,
        "equipment_name": eq.name if eq else None,
        "plan_name": p.plan_name,
        "maintain_type": p.maintain_type,
        "trigger_type": p.trigger_type,
        "trigger_hours": float(p.trigger_hours) if p.trigger_hours else None,
        "trigger_days": p.trigger_days,
        "advance_notify_days": p.advance_notify_days,
        "advance_notify_hours": float(p.advance_notify_hours) if p.advance_notify_hours else None,
        "is_active": p.is_active,
        "last_triggered_at": p.last_triggered_at.isoformat() if p.last_triggered_at else None,
    }


def create_plan(db: Session, req: MaintenancePlanCreate) -> MaintenancePlan:
    plan = MaintenancePlan(**req.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db: Session, plan_id: int, req: dict) -> Optional[MaintenancePlan]:
    plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    if not plan:
        return None
    for k, v in req.items():
        if hasattr(plan, k):
            setattr(plan, k, v)
    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, plan_id: int) -> bool:
    plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True


def list_records(db: Session, equipment_id: int = None, page: int = 1, page_size: int = 20) -> dict:
    q = db.query(MaintenanceRecord)
    if equipment_id:
        q = q.filter(MaintenanceRecord.equipment_id == equipment_id)
    total = q.count()
    items = q.order_by(MaintenanceRecord.maintain_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "list": [_record_to_dict(db, r) for r in items]}


def _record_to_dict(db: Session, r: MaintenanceRecord) -> dict:
    eq = db.query(Equipment).filter(Equipment.id == r.equipment_id).first()
    return {
        "id": r.id,
        "equipment_id": r.equipment_id,
        "equipment_name": eq.name if eq else None,
        "plan_id": r.plan_id,
        "maintain_type": r.maintain_type,
        "maintain_date": str(r.maintain_date) if r.maintain_date else None,
        "running_hours": float(r.running_hours) if r.running_hours else None,
        "cost": float(r.cost) if r.cost else None,
        "parts_replaced": r.parts_replaced,
        "maintainer": r.maintainer,
        "description": r.description,
        "result": r.result,
        "photos": r.photos,
        "report_url": r.report_url,
        "next_maintain_date": str(r.next_maintain_date) if r.next_maintain_date else None,
        "next_maintain_hours": float(r.next_maintain_hours) if r.next_maintain_hours else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def create_record(db: Session, req: MaintenanceRecordCreate, user_id: int) -> MaintenanceRecord:
    """新增维保记录——同时更新设备上次保养日期/台时"""
    record = MaintenanceRecord(**req.model_dump(), created_by=user_id)
    db.add(record)

    # 更新设备维保信息
    eq = db.query(Equipment).filter(Equipment.id == req.equipment_id).first()
    if eq:
        eq.last_maintain_date = req.maintain_date
        if req.running_hours:
            eq.last_maintain_hours = req.running_hours
        # 如果有维保计划，标记相关提醒为已维保
        if req.plan_id:
            reminders = db.query(MaintenanceReminder).filter(
                MaintenanceReminder.plan_id == req.plan_id,
                MaintenanceReminder.status.in_([0, 1]),
            ).all()
            for r in reminders:
                r.status = 2  # 已维保

    db.commit()
    db.refresh(record)
    return record


def list_reminders(db: Session, status: int = None, page: int = 1, page_size: int = 20) -> dict:
    q = db.query(MaintenanceReminder)
    if status is not None:
        q = q.filter(MaintenanceReminder.status == status)
    total = q.count()
    items = q.order_by(MaintenanceReminder.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for r in items:
        eq = db.query(Equipment).filter(Equipment.id == r.equipment_id).first()
        plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == r.plan_id).first()
        result.append({
            "id": r.id,
            "equipment_id": r.equipment_id,
            "equipment_name": eq.name if eq else None,
            "plan_id": r.plan_id,
            "plan_name": plan.plan_name if plan else None,
            "reminder_type": r.reminder_type,
            "target_date": str(r.target_date) if r.target_date else None,
            "target_hours": float(r.target_hours) if r.target_hours else None,
            "status": r.status,
            "notified_at": r.notified_at.isoformat() if r.notified_at else None,
        })
    return {"total": total, "page": page, "page_size": page_size, "list": result}


def action_reminder(db: Session, reminder_id: int, action: str) -> bool:
    r = db.query(MaintenanceReminder).filter(MaintenanceReminder.id == reminder_id).first()
    if not r:
        return False
    if action == "done":
        r.status = 2
    elif action == "ignore":
        r.status = 3
    db.commit()
    return True


# ============ 自动提醒检查 ============

def _has_active_reminder(db: Session, equipment_id: int, plan_id: int) -> bool:
    return db.query(MaintenanceReminder).filter(
        MaintenanceReminder.equipment_id == equipment_id,
        MaintenanceReminder.plan_id == plan_id,
        MaintenanceReminder.status.in_([0, 1]),
    ).first() is not None


def _create_reminder_and_notify(db: Session, equipment_id: int, plan_id: int,
                                 reminder_type: int, target_date=None, target_hours=None):
    """创建提醒 + 通知"""
    if _has_active_reminder(db, equipment_id, plan_id):
        return

    reminder = MaintenanceReminder(
        equipment_id=equipment_id,
        plan_id=plan_id,
        reminder_type=reminder_type,
        target_date=target_date,
        target_hours=target_hours,
        status=1,
        notified_at=datetime.now(),
    )
    db.add(reminder)

    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
    eq_name = eq.name if eq else "未知设备"
    plan_name = plan.plan_name if plan else "维保计划"

    type_text = "日历到期" if reminder_type == 2 else "台时达标"
    title = f"维保提醒: {eq_name} - {plan_name}"
    content = f"设备【{eq_name}】的维保计划【{plan_name}】已{type_text}"
    if target_date:
        content += f"，目标维保日期: {target_date}"
    if target_hours:
        content += f"，目标台时: {target_hours}小时"

    # 通知所有管理员
    from app.models.sys_user import SysUser
    admins = db.query(SysUser).join(SysUser.role).filter(
        SysUser.role.has(role_code="admin")
    ).all() if False else db.query(SysUser).all()  # 简化：通知所有用户
    for admin in admins:
        notif = Notification(
            user_id=admin.id,
            title=title,
            content=content,
            type="maintenance_reminder",
            ref_type="equipment",
            ref_id=equipment_id,
        )
        db.add(notif)

    db.commit()


def check_maintenance_by_calendar(db: Session):
    """日历周期维保检查——每日凌晨执行"""
    today = date.today()
    plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.is_active == 1,
        MaintenancePlan.trigger_type.in_([2, 3]),
    ).all()

    triggered = 0
    for plan in plans:
        # 计算目标维保日期
        last_record = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.equipment_id == plan.equipment_id,
            MaintenanceRecord.plan_id == plan.id,
        ).order_by(MaintenanceRecord.maintain_date.desc()).first()

        if last_record and last_record.maintain_date:
            target_date = last_record.maintain_date + timedelta(days=plan.trigger_days)
        else:
            eq = db.query(Equipment).filter(Equipment.id == plan.equipment_id).first()
            base_date = eq.put_use_date if eq and eq.put_use_date else today
            target_date = base_date + timedelta(days=plan.trigger_days) if base_date else None

        if not target_date:
            continue

        days_until = (target_date - today).days
        if 0 <= days_until <= plan.advance_notify_days:
            _create_reminder_and_notify(db, plan.equipment_id, plan.id, 2, target_date=target_date)
            plan.last_triggered_at = datetime.now()
            triggered += 1

    db.commit()
    return triggered


def check_maintenance_by_hours(db: Session):
    """台时维保检查——每次运转/加油提交后或每小时执行"""
    plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.is_active == 1,
        MaintenancePlan.trigger_type.in_([1, 3]),
    ).all()

    triggered = 0
    for plan in plans:
        eq = db.query(Equipment).filter(Equipment.id == plan.equipment_id).first()
        if not eq:
            continue
        current_hours = float(eq.total_running_hours or 0)
        last_hours = float(eq.last_maintain_hours or 0)
        hours_since = current_hours - last_hours

        if plan.trigger_hours and hours_since >= (float(plan.trigger_hours) - float(plan.advance_notify_hours or 0)):
            _create_reminder_and_notify(db, plan.equipment_id, plan.id, 1, target_hours=plan.trigger_hours)
            plan.last_triggered_at = datetime.now()
            triggered += 1

    db.commit()
    return triggered
