"""特种设备管理路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_dep
from app.models.sys_user import SysUser
from app.services.special_equipment_service import (
    get_special_ext, upsert_special_ext, check_compliance, list_special_equipment,
)
from app.schemas.business import SpecialEquipmentExtCreate
from app.schemas.common import ResponseBase

router = APIRouter(prefix="/special-equipment", tags=["特种设备管理"])


@router.get("")
def list_special(page: int = 1, page_size: int = 20, compliance_status: int = None,
                 db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    result = list_special_equipment(db, page, page_size, compliance_status)
    return ResponseBase.success(result)


@router.get("/{equipment_id}")
def get_special_detail(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    ext = get_special_ext(db, equipment_id)
    if not ext:
        return ResponseBase.error("该设备未配置特种设备扩展信息")
    return ResponseBase.success({
        "id": ext.id,
        "equipment_id": ext.equipment_id,
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
    })


@router.post("/{equipment_id}")
def upsert_special(equipment_id: int, req: SpecialEquipmentExtCreate,
                   db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    req.equipment_id = equipment_id
    ext = upsert_special_ext(db, req)
    return ResponseBase.success({"id": ext.id, "compliance_status": ext.compliance_status}, "保存成功")


@router.post("/{equipment_id}/check")
def check_compliance_api(equipment_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    result = check_compliance(db, equipment_id)
    return ResponseBase.success(result)


@router.get("/compliance-report/all")
def compliance_report(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    """合规报告总览"""
    result = list_special_equipment(db, 1, 1000)
    return ResponseBase.success({
        "total": result["total"],
        "list": result["list"],
    })
