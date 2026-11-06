"""运转记录服务（含台时自动累加）"""
from datetime import date as date_type
from typing import Optional
from sqlalchemy.orm import Session
from app.models.operation import OperationLog
from app.models.equipment import Equipment
from app.schemas.business import OperationLogCreate
from app.services.maintenance_service import check_maintenance_by_hours


def list_operation_logs(db: Session, equipment_id: int = None, page: int = 1, page_size: int = 20,
                        start_date: str = None, end_date: str = None) -> dict:
    q = db.query(OperationLog)
    if equipment_id:
        q = q.filter(OperationLog.equipment_id == equipment_id)
    if start_date:
        q = q.filter(OperationLog.log_date >= start_date)
    if end_date:
        q = q.filter(OperationLog.log_date <= end_date)

    total = q.count()
    items = q.order_by(OperationLog.log_date.desc(), OperationLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for log in items:
        eq = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()
        result.append({
            "id": log.id,
            "equipment_id": log.equipment_id,
            "equipment_name": eq.name if eq else None,
            "log_date": str(log.log_date) if log.log_date else None,
            "shift": log.shift,
            "start_hours": float(log.start_hours) if log.start_hours else None,
            "end_hours": float(log.end_hours) if log.end_hours else None,
            "running_hours": float(log.running_hours) if log.running_hours else None,
            "work_content": log.work_content,
            "work_location": log.work_location,
            "operator_name": log.operator_name,
            "handover_to": log.handover_to,
            "handover_status": log.handover_status,
            "handover_time": log.handover_time.isoformat() if log.handover_time else None,
            "equipment_condition": log.equipment_condition,
            "safety_check": log.safety_check,
            "safety_issues": log.safety_issues,
            "photos": log.photos,
            "remark": log.remark,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })
    return {"total": total, "page": page, "page_size": page_size, "list": result}


def create_operation_log(db: Session, req: OperationLogCreate, user_id: int) -> OperationLog:
    """新增运转记录——自动计算本次台时 + 累加到设备总台时"""
    running_hours = None
    if req.start_hours and req.end_hours:
        running_hours = float(req.end_hours) - float(req.start_hours)
        if running_hours < 0:
            raise ValueError("收工台时不能小于开工台时")

    log = OperationLog(
        equipment_id=req.equipment_id,
        log_date=req.log_date,
        shift=req.shift,
        start_hours=req.start_hours,
        end_hours=req.end_hours,
        running_hours=running_hours,
        work_content=req.work_content,
        work_location=req.work_location,
        operator_name=req.operator_name,
        operator_user_id=user_id,
        handover_to=req.handover_to,
        equipment_condition=req.equipment_condition,
        safety_check=req.safety_check,
        safety_issues=req.safety_issues,
        photos=req.photos,
        remark=req.remark,
    )
    db.add(log)

    # 累加设备总台时
    if running_hours and running_hours > 0:
        eq = db.query(Equipment).filter(Equipment.id == req.equipment_id).first()
        if eq:
            eq.total_running_hours = float(eq.total_running_hours or 0) + running_hours

    db.commit()
    db.refresh(log)

    # 触发维保台时检查
    check_maintenance_by_hours(db)

    return log


def get_today_logs(db: Session, user_id: int) -> list:
    """获取今日运转记录（小程序用）"""
    today = date_type.today()
    logs = db.query(OperationLog).filter(
        OperationLog.operator_user_id == user_id,
        OperationLog.log_date == today,
    ).order_by(OperationLog.id.desc()).all()
    result = []
    for log in logs:
        eq = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()
        result.append({
            "id": log.id,
            "equipment_id": log.equipment_id,
            "equipment_name": eq.name if eq else None,
            "log_date": str(log.log_date),
            "shift": log.shift,
            "running_hours": float(log.running_hours) if log.running_hours else None,
            "work_content": log.work_content,
        })
    return result
