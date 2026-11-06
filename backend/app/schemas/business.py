"""特种设备、维保、加油、运转、报修、培训 Schema"""
from typing import Optional, List, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


# ============ 特种设备 ============
class SpecialEquipmentExtBase(BaseModel):
    registration_number: Optional[str] = None
    registration_cert_url: Optional[str] = None
    registration_date: Optional[date] = None
    registration_expiry: Optional[date] = None
    inspection_type: Optional[str] = None
    last_inspection_date: Optional[date] = None
    next_inspection_date: Optional[date] = None
    inspection_report_url: Optional[str] = None
    inspection_status: Optional[int] = 0
    operator_name: Optional[str] = None
    operator_cert_number: Optional[str] = None
    operator_cert_url: Optional[str] = None
    operator_cert_expiry: Optional[date] = None
    install_dismantle_plan_url: Optional[str] = None
    install_dismantle_plan_date: Optional[date] = None
    acceptance_record_url: Optional[str] = None
    acceptance_date: Optional[date] = None
    acceptance_status: Optional[int] = 0
    supervision_agency: Optional[str] = None
    remark: Optional[str] = None


class SpecialEquipmentExtCreate(SpecialEquipmentExtBase):
    equipment_id: int


class SpecialEquipmentExtOut(SpecialEquipmentExtBase):
    id: int
    equipment_id: int
    compliance_status: Optional[int] = 0
    compliance_issues: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 维保 ============
class MaintenancePlanBase(BaseModel):
    equipment_id: int
    plan_name: str
    maintain_type: Optional[str] = "periodic"
    trigger_type: int = 2
    trigger_hours: Optional[Decimal] = None
    trigger_days: Optional[int] = None
    advance_notify_days: Optional[int] = 7
    advance_notify_hours: Optional[Decimal] = 10
    is_active: Optional[int] = 1


class MaintenancePlanCreate(MaintenancePlanBase):
    pass


class MaintenancePlanOut(MaintenancePlanBase):
    id: int
    last_triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaintenanceRecordBase(BaseModel):
    equipment_id: int
    plan_id: Optional[int] = None
    maintain_type: Optional[str] = "periodic"
    maintain_date: date
    running_hours: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    parts_replaced: Optional[str] = None
    maintainer: Optional[str] = None
    description: Optional[str] = None
    result: Optional[int] = 1
    photos: Optional[str] = None
    report_url: Optional[str] = None
    next_maintain_date: Optional[date] = None
    next_maintain_hours: Optional[Decimal] = None


class MaintenanceRecordCreate(MaintenanceRecordBase):
    pass


class MaintenanceRecordOut(MaintenanceRecordBase):
    id: int
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True


class MaintenanceReminderOut(BaseModel):
    id: int
    equipment_id: int
    plan_id: int
    reminder_type: int
    target_date: Optional[date] = None
    target_hours: Optional[Decimal] = None
    status: int
    notified_at: Optional[datetime] = None
    equipment_name: Optional[str] = None
    plan_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReminderActionRequest(BaseModel):
    action: str  # done / ignore


# ============ 加油 ============
class FuelRecordBase(BaseModel):
    equipment_id: int
    fuel_date: datetime
    fuel_type: Optional[str] = "0#柴油"
    volume: Decimal
    unit_price: Optional[Decimal] = None
    running_hours: Optional[Decimal] = None
    operator_name: Optional[str] = None
    refueling_station: Optional[str] = None
    photo_url: Optional[str] = None
    remark: Optional[str] = None
    source: Optional[int] = 1


class FuelRecordCreate(FuelRecordBase):
    pass


class FuelRecordOut(FuelRecordBase):
    id: int
    total_amount: Optional[Decimal] = None
    previous_hours: Optional[Decimal] = None
    fuel_consumption: Optional[Decimal] = None
    equipment_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 运转记录 ============
class OperationLogBase(BaseModel):
    equipment_id: int
    log_date: date
    shift: Optional[int] = 1
    start_hours: Optional[Decimal] = None
    end_hours: Optional[Decimal] = None
    work_content: Optional[str] = None
    work_location: Optional[str] = None
    operator_name: Optional[str] = None
    handover_to: Optional[str] = None
    equipment_condition: Optional[str] = None
    safety_check: Optional[int] = 1
    safety_issues: Optional[str] = None
    photos: Optional[str] = None
    remark: Optional[str] = None


class OperationLogCreate(OperationLogBase):
    pass


class OperationLogOut(OperationLogBase):
    id: int
    running_hours: Optional[Decimal] = None
    handover_status: Optional[int] = 0
    handover_time: Optional[datetime] = None
    equipment_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 报修 ============
class RepairRequestBase(BaseModel):
    equipment_id: int
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    fault_type: Optional[str] = "其他"
    fault_level: Optional[int] = 1
    fault_description: Optional[str] = None
    fault_photos: Optional[str] = None


class RepairRequestCreate(RepairRequestBase):
    pass


class RepairRequestOut(BaseModel):
    id: int
    request_no: Optional[str] = None
    equipment_id: int
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    fault_type: Optional[str] = None
    fault_level: Optional[int] = None
    fault_description: Optional[str] = None
    fault_photos: Optional[str] = None
    status: Optional[int] = 0
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approve_remark: Optional[str] = None
    repairer: Optional[str] = None
    repair_start: Optional[datetime] = None
    repair_end: Optional[datetime] = None
    repair_description: Optional[str] = None
    repair_parts: Optional[str] = None
    repair_cost: Optional[Decimal] = None
    repair_photos: Optional[str] = None
    downtime_hours: Optional[Decimal] = None
    equipment_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RepairActionRequest(BaseModel):
    action: str  # approve / start_repair / complete / reject
    approve_remark: Optional[str] = None
    repairer: Optional[str] = None
    repair_description: Optional[str] = None
    repair_parts: Optional[str] = None
    repair_cost: Optional[Decimal] = None
    repair_photos: Optional[str] = None


# ============ 培训 ============
class TrainingPlanBase(BaseModel):
    plan_name: str
    training_type: Optional[str] = "安全操作"
    target_audience: Optional[str] = None
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    duration_hours: Optional[Decimal] = None
    instructor: Optional[str] = None
    location: Optional[str] = None
    content_summary: Optional[str] = None
    material_urls: Optional[str] = None
    status: Optional[int] = 0


class TrainingPlanCreate(TrainingPlanBase):
    pass


class TrainingPlanOut(TrainingPlanBase):
    id: int
    participant_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TrainingParticipantBase(BaseModel):
    training_id: int
    user_name: str
    user_id: Optional[int] = None
    attendance: Optional[int] = 1
    exam_score: Optional[Decimal] = None
    exam_passed: Optional[int] = None
    certificate_url: Optional[str] = None
    remark: Optional[str] = None


class TrainingParticipantCreate(TrainingParticipantBase):
    pass


class TrainingParticipantOut(TrainingParticipantBase):
    id: int

    class Config:
        from_attributes = True
