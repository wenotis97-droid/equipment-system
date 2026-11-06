"""加油记录模型"""
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class FuelRecord(Base, BaseModel):
    """加油记录表"""
    __tablename__ = "fuel_record"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    fuel_date = Column(DateTime, nullable=False, comment="加油时间")
    fuel_type = Column(String(32), comment="油品: 0#柴油/汽油等")
    volume = Column(DECIMAL(10, 2), nullable=False, comment="加油量(升)")
    unit_price = Column(DECIMAL(8, 2), comment="单价")
    total_amount = Column(DECIMAL(12, 2), comment="总金额")
    running_hours = Column(DECIMAL(10, 1), comment="加油时台时读数")
    previous_hours = Column(DECIMAL(10, 1), comment="上次加油时台时")
    fuel_consumption = Column(DECIMAL(10, 2), comment="本次油耗(升/小时,自动计算)")
    operator_name = Column(String(64), comment="加油人")
    refueling_station = Column(String(128), comment="加油站")
    photo_url = Column(String(512), comment="加油小票照片")
    remark = Column(String(255), comment="备注")
    source = Column(Integer, default=1, comment="1小程序扫码 2后台录入")
    user_id = Column(Integer, comment="操作人ID")

    equipment = relationship("Equipment", back_populates="fuel_records")
