"""设备相关 Schema"""
from typing import Optional, List, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class EquipmentCategoryBase(BaseModel):
    category_name: str
    parent_id: Optional[int] = 0
    category_code: Optional[str] = None
    is_special_default: Optional[int] = 0
    icon: Optional[str] = None
    sort_order: Optional[int] = 0


class EquipmentCategoryCreate(EquipmentCategoryBase):
    pass


class EquipmentCategoryOut(EquipmentCategoryBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EquipmentFieldDefBase(BaseModel):
    field_key: str
    field_label: str
    field_type: str = "text"
    field_options: Optional[Any] = None
    category_id: Optional[int] = None
    is_required: Optional[int] = 0
    sort_order: Optional[int] = 0
    is_active: Optional[int] = 1


class EquipmentFieldDefCreate(EquipmentFieldDefBase):
    pass


class EquipmentFieldDefOut(EquipmentFieldDefBase):
    id: int

    class Config:
        from_attributes = True


class EquipmentInsuranceBase(BaseModel):
    insurance_type: Optional[str] = None
    insurance_company: Optional[str] = None
    policy_number: Optional[str] = None
    premium: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    file_url: Optional[str] = None
    status: Optional[int] = 1


class EquipmentInsuranceCreate(EquipmentInsuranceBase):
    equipment_id: int


class EquipmentInsuranceOut(EquipmentInsuranceBase):
    id: int
    equipment_id: int

    class Config:
        from_attributes = True


class EquipmentBase(BaseModel):
    equipment_code: str
    name: str
    model: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    is_special: Optional[int] = 0
    status: Optional[int] = 0
    photo_url: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    put_use_date: Optional[date] = None
    factory_number: Optional[str] = None
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None
    location: Optional[str] = None
    project_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_id_card: Optional[str] = None
    extra_attributes: Optional[dict] = None
    remark: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    is_special: Optional[int] = None
    status: Optional[int] = None
    photo_url: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    put_use_date: Optional[date] = None
    factory_number: Optional[str] = None
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None
    location: Optional[str] = None
    project_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_id_card: Optional[str] = None
    extra_attributes: Optional[dict] = None
    remark: Optional[str] = None


class EquipmentOut(EquipmentBase):
    id: int
    qr_token: Optional[str] = None
    total_running_hours: Optional[Decimal] = 0
    last_maintain_date: Optional[date] = None
    last_maintain_hours: Optional[Decimal] = None
    category_name: Optional[str] = None
    project_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EquipmentDetailOut(EquipmentOut):
    insurances: List[EquipmentInsuranceOut] = []
    special_ext: Optional[Any] = None
    extra_field_defs: List[Any] = []


class StatusChangeRequest(BaseModel):
    status: int


class QrCodeOut(BaseModel):
    equipment_id: int
    qr_token: str
    qr_url: str
    qr_image_url: str
