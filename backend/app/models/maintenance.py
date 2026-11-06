"""维保计划、维保记录、维保提醒模型"""
from sqlalchemy import Column, String, Integer, Text, Date, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class MaintenancePlan(Base, BaseModel):
    """维保计划表"""
    __tablename__ = "maintenance_plan"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    plan_name = Column(String(128), nullable=False, comment="计划名称")
    maintain_type = Column(String(32), comment="维保类型: routine/periodic/major")
    trigger_type = Column(Integer, comment="触发方式: 1按台时 2按日历 3两者皆可")
    trigger_hours = Column(DECIMAL(10, 1), comment="触发台时间隔")
    trigger_days = Column(Integer, comment="触发日历间隔")
    advance_notify_days = Column(Integer, default=7, comment="提前提醒天数")
    advance_notify_hours = Column(DECIMAL(10, 1), default=10, comment="提前提醒台时")
    is_active = Column(Integer, default=1, comment="是否启用")
    last_triggered_at = Column(DateTime, comment="上次触发时间")

    equipment = relationship("Equipment", back_populates="maintenance_plans")
    records = relationship("MaintenanceRecord", back_populates="plan")
    reminders = relationship("MaintenanceReminder", back_populates="plan")


class MaintenanceRecord(Base, BaseModel):
    """维保记录表"""
    __tablename__ = "maintenance_record"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    plan_id = Column(Integer, ForeignKey("maintenance_plan.id"), nullable=True, comment="关联维保计划")
    maintain_type = Column(String(32), comment="维保类型")
    maintain_date = Column(Date, nullable=False, comment="维保日期")
    running_hours = Column(DECIMAL(10, 1), comment="维保时台时读数")
    cost = Column(DECIMAL(12, 2), comment="维保费用")
    parts_replaced = Column(Text, comment="更换配件")
    maintainer = Column(String(64), comment="维保人/单位")
    description = Column(Text, comment="维保内容描述")
    result = Column(Integer, default=1, comment="1完成 2异常")
    photos = Column(Text, comment="维保照片URL列表(JSON)")
    report_url = Column(String(512), comment="维保报告文件")
    next_maintain_date = Column(Date, comment="下次建议维保日期")
    next_maintain_hours = Column(DECIMAL(10, 1), comment="下次建议维保台时")
    created_by = Column(Integer, comment="创建人")

    equipment = relationship("Equipment", back_populates="maintenance_records")
    plan = relationship("MaintenancePlan", back_populates="records")


class MaintenanceReminder(Base, BaseModel):
    """维保提醒记录表"""
    __tablename__ = "maintenance_reminder"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    plan_id = Column(Integer, ForeignKey("maintenance_plan.id"), nullable=False, comment="维保计划ID")
    reminder_type = Column(Integer, comment="1台时触发 2日历触发")
    target_date = Column(Date, comment="目标维保日期")
    target_hours = Column(DECIMAL(10, 1), comment="目标台时")
    status = Column(Integer, default=0, comment="0待处理 1已通知 2已维保 3已忽略")
    notified_at = Column(DateTime, comment="通知时间")

    plan = relationship("MaintenancePlan", back_populates="reminders")
