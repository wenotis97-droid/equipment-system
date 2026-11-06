"""统计服务"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.equipment import Equipment
from app.models.fuel import FuelRecord
from app.models.maintenance import MaintenanceReminder, MaintenanceRecord
from app.models.repair import RepairRequest
from app.models.special_equipment import SpecialEquipmentExt


def dashboard(db: Session) -> dict:
    """仪表盘数据"""
    # 设备汇总
    total_equipment = db.query(Equipment).count()
    status_dist = {}
    for s in range(5):
        status_dist[s] = db.query(Equipment).filter(Equipment.status == s).count()

    # 特种设备
    special_count = db.query(Equipment).filter(Equipment.is_special == 1).count()
    # 合规统计
    compliance_dist = {0: 0, 1: 0, 2: 0, 3: 0}
    special_exts = db.query(SpecialEquipmentExt).all()
    for ext in special_exts:
        compliance_dist[ext.compliance_status] = compliance_dist.get(ext.compliance_status, 0) + 1

    # 维保提醒
    pending_reminders = db.query(MaintenanceReminder).filter(MaintenanceReminder.status.in_([0, 1])).count()

    # 报修
    pending_repairs = db.query(RepairRequest).filter(RepairRequest.status.in_([0, 1, 2])).count()

    # 本月加油
    from datetime import date
    today = date.today()
    month_start = today.replace(day=1)
    month_fuel_volume = db.query(func.sum(FuelRecord.volume)).filter(
        FuelRecord.fuel_date >= month_start,
    ).scalar() or 0

    # 本月维保次数
    month_maintenance_count = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.maintain_date >= month_start,
    ).count()

    return {
        "equipment": {
            "total": total_equipment,
            "status_distribution": {
                "闲置": status_dist.get(0, 0),
                "使用中": status_dist.get(1, 0),
                "维修中": status_dist.get(2, 0),
                "停用": status_dist.get(3, 0),
                "报废": status_dist.get(4, 0),
            },
        },
        "special_equipment": {
            "total": special_count,
            "compliance_distribution": {
                "不合规": compliance_dist.get(0, 0),
                "合规": compliance_dist.get(1, 0),
                "即将过期": compliance_dist.get(2, 0),
                "已过期": compliance_dist.get(3, 0),
            },
        },
        "maintenance": {
            "pending_reminders": pending_reminders,
            "month_count": month_maintenance_count,
        },
        "repair": {
            "pending": pending_repairs,
        },
        "fuel": {
            "month_volume": float(month_fuel_volume),
        },
    }
