"""设备运转记录（交接班）模型"""
from sqlalchemy import Column, String, Integer, Text, Date, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class OperationLog(Base, BaseModel):
    """设备运转记录表"""
    __tablename__ = "operation_log"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    log_date = Column(Date, nullable=False, comment="记录日期")
    shift = Column(Integer, comment="班次 1白班 2夜班")
    start_hours = Column(DECIMAL(10, 1), comment="开工台时读数")
    end_hours = Column(DECIMAL(10, 1), comment="收工台时读数")
    running_hours = Column(DECIMAL(10, 1), comment="本次运转台时(自动计算)")
    work_content = Column(Text, comment="工作内容")
    work_location = Column(String(256), comment="作业地点")
    operator_name = Column(String(64), comment="操作人")
    operator_user_id = Column(Integer, comment="操作人系统ID")
    handover_to = Column(String(64), comment="交接班接收人")
    handover_user_id = Column(Integer, comment="接收人系统ID")
    handover_time = Column(DateTime, comment="交接时间")
    handover_status = Column(Integer, default=0, comment="0待交接 1已交接 2已确认")
    equipment_condition = Column(Text, comment="设备状况说明")
    safety_check = Column(Integer, comment="安全检查 1通过 0异常")
    safety_issues = Column(Text, comment="安全问题(如有)")
    photos = Column(Text, comment="照片URL列表(JSON)")
    remark = Column(Text, comment="备注")

    equipment = relationship("Equipment", back_populates="operation_logs")
