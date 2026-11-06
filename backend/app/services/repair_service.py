"""报修管理服务"""
from datetime import datetime
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.repair import RepairRequest
from app.models.equipment import Equipment
from app.schemas.business import RepairRequestCreate, RepairActionRequest


def _gen_request_no() -> str:
    """生成报修单号: WX + 年月日 + 4位随机"""
    return f"WX{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"


def _to_dict(db: Session, r: RepairRequest) -> dict:
    eq = db.query(Equipment).filter(Equipment.id == r.equipment_id).first()
    return {
        "id": r.id,
        "request_no": r.request_no,
        "equipment_id": r.equipment_id,
        "equipment_name": eq.name if eq else None,
        "reporter_name": r.reporter_name,
        "reporter_phone": r.reporter_phone,
        "fault_type": r.fault_type,
        "fault_level": r.fault_level,
        "fault_description": r.fault_description,
        "fault_photos": r.fault_photos,
        "status": r.status,
        "approved_by": r.approved_by,
        "approved_at": r.approved_at.isoformat() if r.approved_at else None,
        "approve_remark": r.approve_remark,
        "repairer": r.repairer,
        "repair_start": r.repair_start.isoformat() if r.repair_start else None,
        "repair_end": r.repair_end.isoformat() if r.repair_end else None,
        "repair_description": r.repair_description,
        "repair_parts": r.repair_parts,
        "repair_cost": float(r.repair_cost) if r.repair_cost else None,
        "repair_photos": r.repair_photos,
        "downtime_hours": float(r.downtime_hours) if r.downtime_hours else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def list_repairs(db: Session, status: int = None, equipment_id: int = None,
                 page: int = 1, page_size: int = 20) -> dict:
    q = db.query(RepairRequest)
    if status is not None:
        q = q.filter(RepairRequest.status == status)
    if equipment_id:
        q = q.filter(RepairRequest.equipment_id == equipment_id)
    total = q.count()
    items = q.order_by(RepairRequest.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "list": [_to_dict(db, r) for r in items]}


def get_repair(db: Session, repair_id: int) -> Optional[dict]:
    r = db.query(RepairRequest).filter(RepairRequest.id == repair_id).first()
    if not r:
        return None
    return _to_dict(db, r)


def create_repair(db: Session, req: RepairRequestCreate, user_id: int) -> RepairRequest:
    repair = RepairRequest(
        request_no=_gen_request_no(),
        equipment_id=req.equipment_id,
        reporter_name=req.reporter_name,
        reporter_user_id=user_id,
        reporter_phone=req.reporter_phone,
        fault_type=req.fault_type,
        fault_level=req.fault_level,
        fault_description=req.fault_description,
        fault_photos=req.fault_photos,
        status=0,
    )
    db.add(repair)

    # 如果设备状态不是维修中，改为维修中（仅当故障等级为紧急/严重）
    if req.fault_level and req.fault_level >= 2:
        eq = db.query(Equipment).filter(Equipment.id == req.equipment_id).first()
        if eq and eq.status != 2:
            eq.status = 2

    db.commit()
    db.refresh(repair)
    return repair


def action_repair(db: Session, repair_id: int, req: RepairActionRequest, user_id: int) -> Optional[RepairRequest]:
    r = db.query(RepairRequest).filter(RepairRequest.id == repair_id).first()
    if not r:
        return None

    if req.action == "approve":
        r.status = 1
        r.approved_by = user_id
        r.approved_at = datetime.now()
        r.approve_remark = req.approve_remark
    elif req.action == "start_repair":
        r.status = 2
        r.repairer = req.repairer
        r.repair_start = datetime.now()
    elif req.action == "complete":
        r.status = 3
        r.repair_end = datetime.now()
        r.repair_description = req.repair_description
        r.repair_parts = req.repair_parts
        r.repair_cost = req.repair_cost
        r.repair_photos = req.repair_photos
        if r.repair_start:
            r.downtime_hours = round((r.repair_end - r.repair_start).total_seconds() / 3600, 1)
        # 设备状态恢复为闲置
        eq = db.query(Equipment).filter(Equipment.id == r.equipment_id).first()
        if eq and eq.status == 2:
            eq.status = 0
    elif req.action == "reject":
        r.status = 4
        r.approved_by = user_id
        r.approved_at = datetime.now()
        r.approve_remark = req.approve_remark

    db.commit()
    db.refresh(r)
    return r


def my_repairs(db: Session, user_id: int) -> list:
    items = db.query(RepairRequest).filter(RepairRequest.reporter_user_id == user_id).order_by(RepairRequest.id.desc()).limit(50).all()
    return [_to_dict(db, r) for r in items]
