"""设备管理服务"""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.equipment import Equipment, EquipmentCategory, EquipmentFieldDef, EquipmentInsurance
from app.models.misc import Project
from app.utils.qrcode_gen import generate_qr_token, generate_qr_code
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


def list_equipment(db: Session, page: int = 1, page_size: int = 20,
                   keyword: str = None, category_id: int = None, is_special: int = None,
                   status: int = None) -> dict:
    """设备列表（分页 + 筛选）"""
    q = db.query(Equipment)
    if keyword:
        q = q.filter(or_(
            Equipment.name.contains(keyword),
            Equipment.equipment_code.contains(keyword),
            Equipment.model.contains(keyword),
        ))
    if category_id:
        q = q.filter(Equipment.category_id == category_id)
    if is_special is not None:
        q = q.filter(Equipment.is_special == is_special)
    if status is not None:
        q = q.filter(Equipment.status == status)

    total = q.count()
    items = q.order_by(Equipment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for eq in items:
        d = _equipment_to_dict(eq)
        result.append(d)

    return {"total": total, "page": page, "page_size": page_size, "list": result}


def _equipment_to_dict(eq: Equipment) -> dict:
    return {
        "id": eq.id,
        "equipment_code": eq.equipment_code,
        "qr_token": eq.qr_token,
        "name": eq.name,
        "model": eq.model,
        "brand": eq.brand,
        "category_id": eq.category_id,
        "category_name": eq.category.category_name if eq.category else None,
        "is_special": eq.is_special,
        "status": eq.status,
        "photo_url": eq.photo_url,
        "purchase_date": str(eq.purchase_date) if eq.purchase_date else None,
        "purchase_price": float(eq.purchase_price) if eq.purchase_price else None,
        "put_use_date": str(eq.put_use_date) if eq.put_use_date else None,
        "factory_number": eq.factory_number,
        "engine_number": eq.engine_number,
        "chassis_number": eq.chassis_number,
        "location": eq.location,
        "project_id": eq.project_id,
        "project_name": eq.project.project_name if eq.project else None,
        "driver_name": eq.driver_name,
        "driver_phone": eq.driver_phone,
        "driver_id_card": eq.driver_id_card,
        "total_running_hours": float(eq.total_running_hours) if eq.total_running_hours else 0,
        "last_maintain_date": str(eq.last_maintain_date) if eq.last_maintain_date else None,
        "last_maintain_hours": float(eq.last_maintain_hours) if eq.last_maintain_hours else None,
        "extra_attributes": eq.extra_attributes,
        "remark": eq.remark,
        "created_at": eq.created_at.isoformat() if eq.created_at else None,
    }


def get_equipment_detail(db: Session, equipment_id: int) -> Optional[dict]:
    """设备详情（含保险、特种设备扩展、扩展字段定义）"""
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return None

    d = _equipment_to_dict(eq)

    # 保险信息
    d["insurances"] = [{
        "id": ins.id,
        "insurance_type": ins.insurance_type,
        "insurance_company": ins.insurance_company,
        "policy_number": ins.policy_number,
        "premium": float(ins.premium) if ins.premium else None,
        "start_date": str(ins.start_date) if ins.start_date else None,
        "end_date": str(ins.end_date) if ins.end_date else None,
        "file_url": ins.file_url,
        "status": ins.status,
    } for ins in eq.insurances]

    # 特种设备扩展
    if eq.is_special == 1 and eq.special_ext:
        ext = eq.special_ext
        d["special_ext"] = {
            "id": ext.id,
            "registration_number": ext.registration_number,
            "registration_cert_url": ext.registration_cert_url,
            "registration_date": str(ext.registration_date) if ext.registration_date else None,
            "registration_expiry": str(ext.registration_expiry) if ext.registration_expiry else None,
            "inspection_type": ext.inspection_type,
            "last_inspection_date": str(ext.last_inspection_date) if ext.last_inspection_date else None,
            "next_inspection_date": str(ext.next_inspection_date) if ext.next_inspection_date else None,
            "inspection_report_url": ext.inspection_report_url,
            "inspection_status": ext.inspection_status,
            "operator_name": ext.operator_name,
            "operator_cert_number": ext.operator_cert_number,
            "operator_cert_url": ext.operator_cert_url,
            "operator_cert_expiry": str(ext.operator_cert_expiry) if ext.operator_cert_expiry else None,
            "install_dismantle_plan_url": ext.install_dismantle_plan_url,
            "install_dismantle_plan_date": str(ext.install_dismantle_plan_date) if ext.install_dismantle_plan_date else None,
            "acceptance_record_url": ext.acceptance_record_url,
            "acceptance_date": str(ext.acceptance_date) if ext.acceptance_date else None,
            "acceptance_status": ext.acceptance_status,
            "supervision_agency": ext.supervision_agency,
            "compliance_status": ext.compliance_status,
            "compliance_issues": ext.compliance_issues,
            "remark": ext.remark,
        }
    else:
        d["special_ext"] = None

    # 扩展字段定义
    field_defs = db.query(EquipmentFieldDef).filter(
        or_(
            EquipmentFieldDef.category_id == eq.category_id,
            EquipmentFieldDef.category_id.is_(None),
        ),
        EquipmentFieldDef.is_active == 1,
    ).order_by(EquipmentFieldDef.sort_order).all()
    d["extra_field_defs"] = [{
        "id": fd.id,
        "field_key": fd.field_key,
        "field_label": fd.field_label,
        "field_type": fd.field_type,
        "field_options": fd.field_options,
        "is_required": fd.is_required,
    } for fd in field_defs]

    return d


def create_equipment(db: Session, req: EquipmentCreate, user_id: int) -> Equipment:
    """创建设备（自动生成二维码 token）"""
    qr_token = generate_qr_token()
    eq = Equipment(
        equipment_code=req.equipment_code,
        qr_token=qr_token,
        name=req.name,
        model=req.model,
        brand=req.brand,
        category_id=req.category_id,
        is_special=req.is_special,
        status=req.status,
        photo_url=req.photo_url,
        purchase_date=req.purchase_date,
        purchase_price=req.purchase_price,
        put_use_date=req.put_use_date,
        factory_number=req.factory_number,
        engine_number=req.engine_number,
        chassis_number=req.chassis_number,
        location=req.location,
        project_id=req.project_id,
        driver_name=req.driver_name,
        driver_phone=req.driver_phone,
        driver_id_card=req.driver_id_card,
        extra_attributes=req.extra_attributes,
        remark=req.remark,
        created_by=user_id,
    )
    db.add(eq)
    db.commit()
    db.refresh(eq)
    return eq


def update_equipment(db: Session, equipment_id: int, req: EquipmentUpdate) -> Optional[Equipment]:
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return None
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(eq, k, v)
    db.commit()
    db.refresh(eq)
    return eq


def delete_equipment(db: Session, equipment_id: int) -> bool:
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return False
    db.delete(eq)
    db.commit()
    return True


def get_equipment_by_qr(db: Session, qr_token: str):
    """通过二维码 token 查设备"""
    return db.query(Equipment).filter(Equipment.qr_token == qr_token).first()


def regenerate_qrcode(db: Session, equipment_id: int) -> Optional[dict]:
    """重新生成二维码（旧 token 失效）"""
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return None
    eq.qr_token = generate_qr_token()
    db.commit()
    db.refresh(eq)
    qr_image_url = generate_qr_code(eq.equipment_code, eq.qr_token)
    return {
        "equipment_id": eq.id,
        "qr_token": eq.qr_token,
        "qr_url": f"{qr_image_url}",
        "qr_image_url": qr_image_url,
    }
