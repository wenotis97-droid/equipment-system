"""特种设备扩展模型（合规管理）"""
from sqlalchemy import Column, String, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class SpecialEquipmentExt(Base, BaseModel):
    """特种设备扩展表——结构化存储合规相关字段"""
    __tablename__ = "special_equipment_ext"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), unique=True, nullable=False, comment="关联设备")
    # 使用登记证
    registration_number = Column(String(128), comment="特种设备使用登记证号")
    registration_cert_url = Column(String(512), comment="使用登记证照片URL")
    registration_date = Column(Date, comment="登记日期")
    registration_expiry = Column(Date, comment="登记有效期")
    # 定期检验
    inspection_type = Column(String(64), comment="检验类型: 首检/定检")
    last_inspection_date = Column(Date, comment="上次检验日期")
    next_inspection_date = Column(Date, comment="下次检验到期日")
    inspection_report_url = Column(String(512), comment="检验报告文件URL")
    inspection_status = Column(Integer, default=0, comment="0未检 1合格 2不合格 3待检")
    # 操作人员特种作业证
    operator_name = Column(String(64), comment="操作人员姓名")
    operator_cert_number = Column(String(128), comment="操作人员特种作业证号")
    operator_cert_url = Column(String(512), comment="作业证照片URL")
    operator_cert_expiry = Column(Date, comment="作业证到期日")
    # 安拆方案
    install_dismantle_plan_url = Column(String(512), comment="安拆方案文件URL")
    install_dismantle_plan_date = Column(Date, comment="安拆方案审批日期")
    # 验收记录
    acceptance_record_url = Column(String(512), comment="验收记录文件URL")
    acceptance_date = Column(Date, comment="验收日期")
    acceptance_status = Column(Integer, default=0, comment="0未验收 1合格 2不合格")
    # 监管与合规状态
    supervision_agency = Column(String(128), comment="监管机构")
    compliance_status = Column(Integer, default=0, comment="0不合规 1合规 2即将过期 3已过期")
    compliance_issues = Column(Text, comment="合规问题清单(JSON字符串)")
    remark = Column(Text, comment="备注")

    equipment = relationship("Equipment", back_populates="special_ext")
