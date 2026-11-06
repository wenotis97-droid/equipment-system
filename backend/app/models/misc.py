"""项目、通知、扫码日志模型"""
from sqlalchemy import Column, String, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class Project(Base, BaseModel):
    """项目表"""
    __tablename__ = "project"

    project_name = Column(String(128), nullable=False, comment="项目名称")
    project_code = Column(String(64), comment="项目编号")
    location = Column(String(256), comment="项目地点")
    start_date = Column(Date, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    status = Column(Integer, default=1, comment="0筹备 1进行中 2完工 3停工")
    manager_id = Column(Integer, comment="项目经理ID")
    manager_name = Column(String(64), comment="项目经理姓名")

    equipments = relationship("Equipment", back_populates="project")


class Notification(Base, BaseModel):
    """消息通知表"""
    __tablename__ = "notification"

    user_id = Column(Integer, comment="接收人ID")
    title = Column(String(128), nullable=False, comment="标题")
    content = Column(Text, comment="内容")
    type = Column(String(32), comment="类型: 维保提醒/报修状态/审批通知/合规预警等")
    ref_type = Column(String(32), comment="关联类型")
    ref_id = Column(Integer, comment="关联ID")
    is_read = Column(Integer, default=0, comment="是否已读 0否 1是")


class QrCodeLog(Base, BaseModel):
    """二维码扫码日志表"""
    __tablename__ = "qr_code_log"

    equipment_id = Column(Integer, comment="设备ID")
    qr_token = Column(String(128), comment="扫码Token")
    user_id = Column(Integer, comment="扫码人(如已登录)")
    wx_openid = Column(String(128), comment="微信openid")
    scan_time = Column(DateTime, comment="扫码时间")
    ip = Column(String(64), comment="IP")
    user_agent = Column(String(256), comment="User-Agent")
