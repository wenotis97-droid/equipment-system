"""安全培训模型"""
from sqlalchemy import Column, String, Integer, Text, DECIMAL, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class TrainingPlan(Base, BaseModel):
    """培训计划表"""
    __tablename__ = "training_plan"

    plan_name = Column(String(128), nullable=False, comment="培训名称")
    training_type = Column(String(64), comment="培训类型: 安全操作/特种作业/法规等")
    target_audience = Column(String(256), comment="培训对象")
    planned_date = Column(DateTime, comment="计划时间")
    actual_date = Column(DateTime, comment="实际时间")
    duration_hours = Column(DECIMAL(5, 1), comment="培训时长")
    instructor = Column(String(64), comment="讲师")
    location = Column(String(256), comment="培训地点")
    content_summary = Column(Text, comment="内容摘要")
    material_urls = Column(Text, comment="培训材料文件URL(JSON)")
    status = Column(Integer, default=0, comment="0计划中 1已发布 2已完成 3已取消")

    participants = relationship("TrainingParticipant", back_populates="training", cascade="all, delete-orphan")


class TrainingParticipant(Base, BaseModel):
    """培训参与记录表"""
    __tablename__ = "training_participant"

    training_id = Column(Integer, ForeignKey("training_plan.id"), nullable=False, comment="培训ID")
    user_id = Column(Integer, comment="参与人")
    user_name = Column(String(64), comment="参与人姓名(冗余)")
    attendance = Column(Integer, comment="0缺席 1出席")
    exam_score = Column(DECIMAL(5, 1), comment="考核分数")
    exam_passed = Column(Integer, comment="0未通过 1通过")
    certificate_url = Column(String(512), comment="培训合格证URL")
    remark = Column(String(255), comment="备注")

    training = relationship("TrainingPlan", back_populates="participants")
