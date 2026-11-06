"""特种设备合规校验服务"""
import json
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models.equipment import Equipment
from app.models.special_equipment import SpecialEquipmentExt
from app.models.misc import Notification
from app.schemas.business import SpecialEquipmentExtCreate


def get_special_ext(db: Session, equipment_id: int) -> Optional[SpecialEquipmentExt]:
    return db.query(SpecialEquipmentExt).filter(SpecialEquipmentExt.equipment_id == equipment_id).first()


def upsert_special_ext(db: Session, req: SpecialEquipmentExtCreate) -> SpecialEquipmentExt:
    """新增或更新特种设备扩展信息"""
    ext = db.query(SpecialEquipmentExt).filter(SpecialEquipmentExt.equipment_id == req.equipment_id).first()
    data = req.model_dump()
    if ext:
        for k, v in data.items():
            setattr(ext, k, v)
    else:
        ext = SpecialEquipmentExt(**data)
        db.add(ext)
        # 确保设备标记为特种设备
        eq = db.query(Equipment).filter(Equipment.id == req.equipment_id).first()
        if eq:
            eq.is_special = 1
    db.commit()
    db.refresh(ext)

    # 实时校验合规
    check_compliance(db, ext.equipment_id)
    return ext


def check_compliance(db: Session, equipment_id: int) -> dict:
    """特种设备合规校验——五项检查"""
    ext = db.query(SpecialEquipmentExt).filter(SpecialEquipmentExt.equipment_id == equipment_id).first()
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()

    if not ext:
        return {"status": 0, "issues": ["未配置特种设备扩展信息"], "warnings": []}

    issues = []
    warnings = []
    today = date.today()

    # 1. 使用登记证
    if not ext.registration_number:
        issues.append("缺少特种设备使用登记证")
    elif ext.registration_expiry and ext.registration_expiry < today:
        issues.append(f"使用登记证已过期（到期日: {ext.registration_expiry}）")
    elif ext.registration_expiry and (ext.registration_expiry - today).days <= 30:
        warnings.append(f"使用登记证即将过期（到期日: {ext.registration_expiry}）")

    # 2. 定期检验报告
    if not ext.last_inspection_date:
        issues.append("缺少定期检验报告")
    elif ext.inspection_status != 1:
        status_text = {0: "未检", 2: "不合格", 3: "待检"}.get(ext.inspection_status, "未知")
        issues.append(f"检验结果{status_text}")
    elif ext.next_inspection_date:
        if ext.next_inspection_date < today:
            issues.append(f"定期检验已过期（应检日: {ext.next_inspection_date}）")
        elif (ext.next_inspection_date - today).days <= 30:
            warnings.append(f"定期检验即将到期（应检日: {ext.next_inspection_date}）")

    # 3. 操作人员特种作业证
    if not ext.operator_cert_number:
        issues.append("缺少操作人员特种作业证")
    elif ext.operator_cert_expiry and ext.operator_cert_expiry < today:
        issues.append(f"操作人员特种作业证已过期（到期日: {ext.operator_cert_expiry}）")
    elif ext.operator_cert_expiry and (ext.operator_cert_expiry - today).days <= 60:
        warnings.append(f"操作人员特种作业证即将过期（到期日: {ext.operator_cert_expiry}）")

    # 4. 安拆方案
    if not ext.install_dismantle_plan_url:
        issues.append("缺少安拆方案")

    # 5. 验收记录
    if not ext.acceptance_record_url:
        issues.append("缺少验收记录")
    elif ext.acceptance_status != 1:
        acc_text = {0: "未验收", 2: "不合格"}.get(ext.acceptance_status, "未知")
        issues.append(f"验收{acc_text}")

    # 计算合规状态: 0不合规 1合规 2即将过期 3已过期
    has_expired = any("已过期" in i for i in issues)
    if has_expired:
        status = 3
    elif issues:
        status = 0
    elif warnings:
        status = 2
    else:
        status = 1

    ext.compliance_status = status
    ext.compliance_issues = json.dumps({"issues": issues, "warnings": warnings}, ensure_ascii=False)
    db.commit()

    # 不合规或已过期 → 通知管理员
    if status in (0, 3) and eq:
        from app.models.sys_user import SysUser
        title = f"特种设备合规预警: {eq.name}"
        content = f"设备【{eq.name}】合规状态异常：\n" + "\n".join(issues[:5])
        admins = db.query(SysUser).filter(SysUser.status == 1).all()
        for admin in admins:
            notif = Notification(
                user_id=admin.id,
                title=title,
                content=content,
                type="compliance_warning",
                ref_type="equipment",
                ref_id=equipment_id,
            )
            db.add(notif)
        db.commit()

    return {"status": status, "issues": issues, "warnings": warnings}


def list_special_equipment(db: Session, page: int = 1, page_size: int = 20, compliance_status: int = None) -> dict:
    """特种设备列表"""
    q = db.query(Equipment).filter(Equipment.is_special == 1)
    total = q.count()
    items = q.order_by(Equipment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for eq in items:
        ext = eq.special_ext
        result.append({
            "id": eq.id,
            "equipment_code": eq.equipment_code,
            "name": eq.name,
            "model": eq.model,
            "location": eq.location,
            "status": eq.status,
            "category_name": eq.category.category_name if eq.category else None,
            "compliance_status": ext.compliance_status if ext else 0,
            "compliance_issues": ext.compliance_issues if ext else None,
            "registration_number": ext.registration_number if ext else None,
            "next_inspection_date": str(ext.next_inspection_date) if ext and ext.next_inspection_date else None,
            "operator_cert_expiry": str(ext.operator_cert_expiry) if ext and ext.operator_cert_expiry else None,
            "special_ext_id": ext.id if ext else None,
        })
    # 筛选合规状态
    if compliance_status is not None:
        result = [r for r in result if r["compliance_status"] == compliance_status]
        total = len(result)
    return {"total": total, "page": page, "page_size": page_size, "list": result}


def check_all_special_compliance(db: Session) -> int:
    """检查所有特种设备合规状态——定时任务用"""
    equipments = db.query(Equipment).filter(Equipment.is_special == 1).all()
    count = 0
    for eq in equipments:
        if eq.special_ext:
            check_compliance(db, eq.id)
            count += 1
    return count
