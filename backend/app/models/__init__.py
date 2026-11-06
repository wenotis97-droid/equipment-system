"""模型汇总，统一导入以便 Alembic 和 create_all 发现所有表"""
from app.models.sys_user import SysUser, SysRole, SysDepartment
from app.models.equipment import Equipment, EquipmentCategory, EquipmentFieldDef, EquipmentInsurance
from app.models.special_equipment import SpecialEquipmentExt
from app.models.maintenance import MaintenancePlan, MaintenanceRecord, MaintenanceReminder
from app.models.fuel import FuelRecord
from app.models.operation import OperationLog
from app.models.repair import RepairRequest
from app.models.training import TrainingPlan, TrainingParticipant
from app.models.misc import Project, Notification, QrCodeLog

__all__ = [
    "SysUser", "SysRole", "SysDepartment",
    "Equipment", "EquipmentCategory", "EquipmentFieldDef", "EquipmentInsurance",
    "SpecialEquipmentExt",
    "MaintenancePlan", "MaintenanceRecord", "MaintenanceReminder",
    "FuelRecord",
    "OperationLog",
    "RepairRequest",
    "TrainingPlan", "TrainingParticipant",
    "Project", "Notification", "QrCodeLog",
]
