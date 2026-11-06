"""设备档案管理路由"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_dep
from app.models.sys_user import SysUser
from app.models.equipment import Equipment, EquipmentCategory, EquipmentFieldDef, EquipmentInsurance
from app.services.equipment_service import (
    list_equipment, get_equipment_detail, create_equipment, update_equipment, delete_equipment,
    get_equipment_by_qr, regenerate_qrcode,
)
from app.utils.qrcode_gen import generate_qr_code, generate_qr_code_bytes
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentInsuranceCreate, StatusChangeRequest
from app.schemas.common import ResponseBase
from datetime import date

router = APIRouter(prefix="/equipment", tags=["设备档案管理"])


@router.get("")
def list_equipment_api(
    page: int = 1, page_size: int = 20,
    keyword: str = None, category_id: int = None,
    is_special: int = None, status: int = None,
    db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep),
):
    result = list_equipment(db, page, page_size, keyword, category_id, is_special, status)
    return ResponseBase.success(result)


@router.post("")
def create_equipment_api(req: EquipmentCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    # 检查编号唯一
    existing = db.query(Equipment).filter(Equipment.equipment_code == req.equipment_code).first()
    if existing:
        return ResponseBase.error("设备编号已存在")
    eq = create_equipment(db, req, user.id)
    # 生成二维码图片
    qr_image_url = generate_qr_code(eq.equipment_code, eq.qr_token)
    return ResponseBase.success({
        "id": eq.id,
        "qr_token": eq.qr_token,
        "qr_image_url": qr_image_url,
    }, "创建成功")


@router.get("/{equipment_id}")
def get_equipment_api(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    detail = get_equipment_detail(db, equipment_id)
    if not detail:
        return ResponseBase.error("设备不存在")
    return ResponseBase.success(detail)


@router.put("/{equipment_id}")
def update_equipment_api(equipment_id: int, req: EquipmentUpdate,
                         db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    eq = update_equipment(db, equipment_id, req)
    if not eq:
        return ResponseBase.error("设备不存在")
    return ResponseBase.success({"id": eq.id}, "更新成功")


@router.delete("/{equipment_id}")
def delete_equipment_api(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    if not delete_equipment(db, equipment_id):
        return ResponseBase.error("设备不存在")
    return ResponseBase.success(message="删除成功")


@router.put("/{equipment_id}/status")
def change_status_api(equipment_id: int, req: StatusChangeRequest,
                      db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return ResponseBase.error("设备不存在")
    eq.status = req.status
    db.commit()
    return ResponseBase.success(message="状态变更成功")


# ============ 二维码 ============
@router.get("/{equipment_id}/qrcode")
def get_qrcode(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return ResponseBase.error("设备不存在")
    # 确保二维码图片存在
    qr_image_url = generate_qr_code(eq.equipment_code, eq.qr_token)
    return ResponseBase.success({
        "equipment_id": eq.id,
        "qr_token": eq.qr_token,
        "qr_url": f"http://localhost:8000/scan?token={eq.qr_token}",
        "qr_image_url": qr_image_url,
    })


@router.get("/{equipment_id}/qrcode/download")
def download_qrcode(equipment_id: int, db: Session = Depends(get_db)):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return ResponseBase.error("设备不存在")
    img_bytes = generate_qr_code_bytes(eq.equipment_code, eq.qr_token)
    return StreamingResponse(
        __import__("io").BytesIO(img_bytes),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=qrcode_{eq.equipment_code}.png"},
    )


@router.post("/{equipment_id}/qrcode/regenerate")
def regenerate_qrcode_api(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    result = regenerate_qrcode(db, equipment_id)
    if not result:
        return ResponseBase.error("设备不存在")
    return ResponseBase.success(result, "二维码已重新生成")


# ============ 保险 ============
@router.get("/{equipment_id}/insurance")
def list_insurance(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    items = db.query(EquipmentInsurance).filter(EquipmentInsurance.equipment_id == equipment_id).all()
    return ResponseBase.success([{
        "id": i.id, "insurance_type": i.insurance_type, "insurance_company": i.insurance_company,
        "policy_number": i.policy_number, "premium": float(i.premium) if i.premium else None,
        "start_date": str(i.start_date) if i.start_date else None,
        "end_date": str(i.end_date) if i.end_date else None,
        "file_url": i.file_url, "status": i.status,
    } for i in items])


@router.post("/{equipment_id}/insurance")
def add_insurance(equipment_id: int, req: EquipmentInsuranceCreate,
                  db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    ins = EquipmentInsurance(
        equipment_id=equipment_id,
        insurance_type=req.insurance_type,
        insurance_company=req.insurance_company,
        policy_number=req.policy_number,
        premium=req.premium,
        start_date=req.start_date,
        end_date=req.end_date,
        file_url=req.file_url,
        status=req.status,
    )
    db.add(ins)
    db.commit()
    return ResponseBase.success({"id": ins.id}, "添加成功")


@router.put("/insurance/{insurance_id}")
def update_insurance(insurance_id: int, req: EquipmentInsuranceCreate,
                     db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    ins = db.query(EquipmentInsurance).filter(EquipmentInsurance.id == insurance_id).first()
    if not ins:
        return ResponseBase.error("保险记录不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(ins, k, v)
    db.commit()
    return ResponseBase.success(message="更新成功")


@router.delete("/insurance/{insurance_id}")
def delete_insurance(insurance_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    ins = db.query(EquipmentInsurance).filter(EquipmentInsurance.id == insurance_id).first()
    if not ins:
        return ResponseBase.error("保险记录不存在")
    db.delete(ins)
    db.commit()
    return ResponseBase.success(message="删除成功")


# ============ 设备类别 ============
@router.get("/categories/all")
def list_categories(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    cats = db.query(EquipmentCategory).order_by(EquipmentCategory.sort_order).all()
    return ResponseBase.success([{
        "id": c.id, "category_name": c.category_name, "parent_id": c.parent_id,
        "category_code": c.category_code, "is_special_default": c.is_special_default,
        "icon": c.icon, "sort_order": c.sort_order,
    } for c in cats])


@router.post("/categories")
def create_category(data: dict, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    cat = EquipmentCategory(
        category_name=data.get("category_name"),
        parent_id=data.get("parent_id", 0),
        category_code=data.get("category_code"),
        is_special_default=data.get("is_special_default", 0),
        sort_order=data.get("sort_order", 0),
    )
    db.add(cat)
    db.commit()
    return ResponseBase.success({"id": cat.id}, "创建成功")


@router.put("/categories/{cat_id}")
def update_category(cat_id: int, data: dict, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    cat = db.query(EquipmentCategory).filter(EquipmentCategory.id == cat_id).first()
    if not cat:
        return ResponseBase.error("类别不存在")
    for k, v in data.items():
        if hasattr(cat, k):
            setattr(cat, k, v)
    db.commit()
    return ResponseBase.success(message="更新成功")


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    cat = db.query(EquipmentCategory).filter(EquipmentCategory.id == cat_id).first()
    if not cat:
        return ResponseBase.error("类别不存在")
    db.delete(cat)
    db.commit()
    return ResponseBase.success(message="删除成功")


# ============ 扩展字段定义 ============
@router.get("/field-defs/all")
def list_field_defs(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    defs = db.query(EquipmentFieldDef).filter(EquipmentFieldDef.is_active == 1).order_by(EquipmentFieldDef.sort_order).all()
    return ResponseBase.success([{
        "id": d.id, "field_key": d.field_key, "field_label": d.field_label,
        "field_type": d.field_type, "field_options": d.field_options,
        "category_id": d.category_id, "is_required": d.is_required,
        "sort_order": d.sort_order,
    } for d in defs])


@router.post("/field-defs")
def create_field_def(data: dict, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    d = EquipmentFieldDef(
        field_key=data.get("field_key"),
        field_label=data.get("field_label"),
        field_type=data.get("field_type", "text"),
        field_options=data.get("field_options"),
        category_id=data.get("category_id"),
        is_required=data.get("is_required", 0),
        sort_order=data.get("sort_order", 0),
    )
    db.add(d)
    db.commit()
    return ResponseBase.success({"id": d.id}, "创建成功")


@router.put("/field-defs/{def_id}")
def update_field_def(def_id: int, data: dict, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    d = db.query(EquipmentFieldDef).filter(EquipmentFieldDef.id == def_id).first()
    if not d:
        return ResponseBase.error("字段定义不存在")
    for k, v in data.items():
        if hasattr(d, k):
            setattr(d, k, v)
    db.commit()
    return ResponseBase.success(message="更新成功")


@router.delete("/field-defs/{def_id}")
def delete_field_def(def_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    d = db.query(EquipmentFieldDef).filter(EquipmentFieldDef.id == def_id).first()
    if not d:
        return ResponseBase.error("字段定义不存在")
    d.is_active = 0
    db.commit()
    return ResponseBase.success(message="已禁用")
