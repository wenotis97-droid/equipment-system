"""加油记录服务（含自动计算油耗）"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.fuel import FuelRecord
from app.models.equipment import Equipment
from app.schemas.business import FuelRecordCreate
from app.services.maintenance_service import check_maintenance_by_hours


def list_fuel_records(db: Session, equipment_id: int = None, page: int = 1, page_size: int = 20,
                      start_date: str = None, end_date: str = None) -> dict:
    q = db.query(FuelRecord)
    if equipment_id:
        q = q.filter(FuelRecord.equipment_id == equipment_id)
    if start_date:
        q = q.filter(FuelRecord.fuel_date >= start_date)
    if end_date:
        q = q.filter(FuelRecord.fuel_date <= end_date)

    total = q.count()
    items = q.order_by(FuelRecord.fuel_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for fr in items:
        eq = db.query(Equipment).filter(Equipment.id == fr.equipment_id).first()
        result.append({
            "id": fr.id,
            "equipment_id": fr.equipment_id,
            "equipment_name": eq.name if eq else None,
            "fuel_date": fr.fuel_date.isoformat() if fr.fuel_date else None,
            "fuel_type": fr.fuel_type,
            "volume": float(fr.volume) if fr.volume else None,
            "unit_price": float(fr.unit_price) if fr.unit_price else None,
            "total_amount": float(fr.total_amount) if fr.total_amount else None,
            "running_hours": float(fr.running_hours) if fr.running_hours else None,
            "previous_hours": float(fr.previous_hours) if fr.previous_hours else None,
            "fuel_consumption": float(fr.fuel_consumption) if fr.fuel_consumption else None,
            "operator_name": fr.operator_name,
            "refueling_station": fr.refueling_station,
            "photo_url": fr.photo_url,
            "remark": fr.remark,
            "source": fr.source,
            "created_at": fr.created_at.isoformat() if fr.created_at else None,
        })
    return {"total": total, "page": page, "page_size": page_size, "list": result}


def create_fuel_record(db: Session, req: FuelRecordCreate, user_id: int) -> FuelRecord:
    """新增加油记录——自动计算总金额和油耗"""
    # 查上次加油记录的台时
    prev = db.query(FuelRecord).filter(
        FuelRecord.equipment_id == req.equipment_id,
    ).order_by(FuelRecord.fuel_date.desc()).first()

    previous_hours = float(prev.running_hours) if prev and prev.running_hours else 0
    total_amount = float(req.volume) * float(req.unit_price) if req.unit_price else None

    # 计算油耗（升/小时）
    fuel_consumption = None
    if req.running_hours and previous_hours:
        hours_diff = float(req.running_hours) - previous_hours
        if hours_diff > 0:
            fuel_consumption = round(float(req.volume) / hours_diff, 2)

    record = FuelRecord(
        equipment_id=req.equipment_id,
        fuel_date=req.fuel_date,
        fuel_type=req.fuel_type,
        volume=req.volume,
        unit_price=req.unit_price,
        total_amount=total_amount,
        running_hours=req.running_hours,
        previous_hours=previous_hours,
        fuel_consumption=fuel_consumption,
        operator_name=req.operator_name,
        refueling_station=req.refueling_station,
        photo_url=req.photo_url,
        remark=req.remark,
        source=req.source or 1,
        user_id=user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 如果提交了台时，触发维保台时检查
    if req.running_hours:
        check_maintenance_by_hours(db)

    return record


def fuel_analysis(db: Session, equipment_id: int = None, start_date: str = None, end_date: str = None) -> dict:
    """油耗分析"""
    q = db.query(FuelRecord)
    if equipment_id:
        q = q.filter(FuelRecord.equipment_id == equipment_id)
    if start_date:
        q = q.filter(FuelRecord.fuel_date >= start_date)
    if end_date:
        q = q.filter(FuelRecord.fuel_date <= end_date)

    records = q.order_by(FuelRecord.fuel_date.asc()).all()

    total_volume = sum(float(r.volume) for r in records if r.volume)
    total_amount = sum(float(r.total_amount) for r in records if r.total_amount)
    avg_consumption = None
    consumptions = [float(r.fuel_consumption) for r in records if r.fuel_consumption]
    if consumptions:
        avg_consumption = round(sum(consumptions) / len(consumptions), 2)

    # 按设备汇总
    by_equipment = {}
    for r in records:
        eq = db.query(Equipment).filter(Equipment.id == r.equipment_id).first()
        name = eq.name if eq else str(r.equipment_id)
        if name not in by_equipment:
            by_equipment[name] = {"volume": 0, "amount": 0, "count": 0}
        by_equipment[name]["volume"] += float(r.volume or 0)
        by_equipment[name]["amount"] += float(r.total_amount or 0)
        by_equipment[name]["count"] += 1

    return {
        "total_volume": round(total_volume, 2),
        "total_amount": round(total_amount, 2),
        "avg_consumption": avg_consumption,
        "record_count": len(records),
        "by_equipment": [{"name": k, **v} for k, v in by_equipment.items()],
    }
