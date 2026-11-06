"""报修管理模型"""
from sqlalchemy import Column, String, Integer, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class RepairRequest(Base, BaseModel):
    """报修申请表"""
    __tablename__ = "repair_request"

    request_no = Column(String(32), unique=True, comment="报修单号(自动生成)")
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    reporter_name = Column(String(64), comment="报修人")
    reporter_user_id = Column(Integer, comment="报修人系统ID")
    reporter_phone = Column(String(20), comment="报修人电话")
    fault_type = Column(String(64), comment="故障类型: 发动机/液压/电气/结构/其他")
    fault_level = Column(Integer, comment="严重程度 1一般 2严重 3紧急")
    fault_description = Column(Text, comment="故障描述")
    fault_photos = Column(Text, comment="故障照片URL列表(JSON)")
    status = Column(Integer, default=0, comment="0待审批 1已审批待维修 2维修中 3已完成 4已驳回")
    approved_by = Column(Integer, comment="审批人")
    approved_at = Column(DateTime, comment="审批时间")
    approve_remark = Column(Text, comment="审批意见")
    repairer = Column(String(64), comment="维修人/单位")
    repair_start = Column(DateTime, comment="维修开始时间")
    repair_end = Column(DateTime, comment="维修结束时间")
    repair_description = Column(Text, comment="维修过程描述")
    repair_parts = Column(Text, comment="更换配件")
    repair_cost = Column(DECIMAL(12, 2), comment="维修费用")
    repair_photos = Column(Text, comment="维修后照片(JSON)")
    downtime_hours = Column(DECIMAL(10, 1), comment="停机时长(小时)")

    equipment = relationship("Equipment", back_populates="repair_requests")
