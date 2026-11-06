"""设备、设备类别、字段定义、保险模型"""
from sqlalchemy import Column, String, Integer, Text, JSON, Integer, ForeignKey, Date, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.database import Base


class EquipmentCategory(Base, BaseModel):
    """设备类别表"""
    __tablename__ = "equipment_category"

    category_name = Column(String(64), nullable=False, comment="类别名称")
    parent_id = Column(Integer, default=0, comment="父类别ID")
    category_code = Column(String(64), comment="类别编码")
    is_special_default = Column(Integer, default=0, comment="该类别默认是否特种设备 0否 1是")
    icon = Column(String(256), comment="图标URL")
    sort_order = Column(Integer, default=0, comment="排序")

    equipments = relationship("Equipment", back_populates="category")
    field_defs = relationship("EquipmentFieldDef", back_populates="category")


class EquipmentFieldDef(Base, BaseModel):
    """设备扩展字段定义表（支持后台动态配置）"""
    __tablename__ = "equipment_field_def"

    field_key = Column(String(64), nullable=False, comment="字段键名")
    field_label = Column(String(128), nullable=False, comment="字段显示名")
    field_type = Column(String(32), nullable=False, comment="类型: text/number/date/select/file")
    field_options = Column(JSON, comment="select类型的选项")
    category_id = Column(Integer, ForeignKey("equipment_category.id"), nullable=True, comment="所属设备类别(NULL=全局)")
    is_required = Column(Integer, default=0, comment="是否必填")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Integer, default=1, comment="是否启用")

    category = relationship("EquipmentCategory", back_populates="field_defs")


class Equipment(Base, BaseModel):
    """设备主表"""
    __tablename__ = "equipment"

    equipment_code = Column(String(64), unique=True, nullable=False, comment="设备编号")
    qr_token = Column(String(128), unique=True, comment="二维码Token")
    name = Column(String(128), nullable=False, comment="设备名称")
    model = Column(String(128), comment="规格型号")
    brand = Column(String(64), comment="品牌/厂家")
    category_id = Column(Integer, ForeignKey("equipment_category.id"), comment="设备类别ID")
    is_special = Column(Integer, default=0, comment="是否特种设备 0否 1是")
    status = Column(Integer, default=0, comment="0闲置 1使用中 2维修中 3停用 4报废")
    photo_url = Column(String(512), comment="设备照片URL")
    purchase_date = Column(Date, comment="购置日期")
    purchase_price = Column(DECIMAL(12, 2), comment="购置价格")
    put_use_date = Column(Date, comment="投用日期")
    factory_number = Column(String(128), comment="出厂编号")
    engine_number = Column(String(128), comment="发动机编号")
    chassis_number = Column(String(128), comment="底盘编号")
    location = Column(String(256), comment="当前存放/使用地点")
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True, comment="所属项目ID")
    driver_name = Column(String(64), comment="驾驶员姓名")
    driver_phone = Column(String(20), comment="驾驶员电话")
    driver_id_card = Column(String(20), comment="驾驶员身份证")
    total_running_hours = Column(DECIMAL(10, 1), default=0, comment="累计运转台时")
    last_maintain_date = Column(Date, comment="上次保养日期")
    last_maintain_hours = Column(DECIMAL(10, 1), comment="上次保养时台时")
    extra_attributes = Column(JSON, comment="扩展属性(灵活字段)")
    remark = Column(Text, comment="备注")
    created_by = Column(Integer, comment="创建人")

    category = relationship("EquipmentCategory", back_populates="equipments")
    project = relationship("Project", back_populates="equipments")
    insurances = relationship("EquipmentInsurance", back_populates="equipment", cascade="all, delete-orphan")
    special_ext = relationship("SpecialEquipmentExt", back_populates="equipment", uselist=False, cascade="all, delete-orphan")
    maintenance_plans = relationship("MaintenancePlan", back_populates="equipment", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment", cascade="all, delete-orphan")
    fuel_records = relationship("FuelRecord", back_populates="equipment", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="equipment", cascade="all, delete-orphan")
    repair_requests = relationship("RepairRequest", back_populates="equipment", cascade="all, delete-orphan")


class EquipmentInsurance(Base, BaseModel):
    """设备保险信息表"""
    __tablename__ = "equipment_insurance"

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    insurance_type = Column(String(64), comment="险种")
    insurance_company = Column(String(128), comment="保险公司")
    policy_number = Column(String(128), comment="保单号")
    premium = Column(DECIMAL(12, 2), comment="保费")
    start_date = Column(Date, comment="起保日期")
    end_date = Column(Date, comment="到期日期")
    file_url = Column(String(512), comment="保单文件URL")
    status = Column(Integer, default=1, comment="1有效 0过期")

    equipment = relationship("Equipment", back_populates="insurances")
