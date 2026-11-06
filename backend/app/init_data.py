"""初始化示例数据——首次启动时自动填充"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.models.sys_user import SysUser, SysRole, SysDepartment
from app.models.equipment import Equipment, EquipmentCategory, EquipmentFieldDef, EquipmentInsurance
from app.models.special_equipment import SpecialEquipmentExt
from app.models.maintenance import MaintenancePlan, MaintenanceRecord, MaintenanceReminder
from app.models.fuel import FuelRecord
from app.models.operation import OperationLog
from app.models.repair import RepairRequest
from app.models.training import TrainingPlan, TrainingParticipant
from app.models.misc import Project
from app.utils.security import hash_password
from app.utils.qrcode_gen import generate_qr_token, generate_qr_code


def init_data(db):
    """初始化示例数据（仅当数据库为空时）"""
    if db.query(SysRole).count() > 0:
        return  # 已有数据，跳过

    print("[初始化] 开始填充示例数据...")

    # ============ 角色 ============
    admin_role = SysRole(role_name="系统管理员", role_code="admin", description="全部权限", permissions=["*"])
    manager_role = SysRole(role_name="设备主管", role_code="manager", description="设备管理权限", permissions=["equipment:*", "maintenance:*", "repair:*"])
    operator_role = SysRole(role_name="操作员", role_code="operator", description="小程序操作权限", permissions=["miniapp:*"])
    driver_role = SysRole(role_name="驾驶员", role_code="driver", description="驾驶员权限", permissions=["miniapp:*"])
    db.add_all([admin_role, manager_role, operator_role, driver_role])
    db.flush()

    # ============ 部门 ============
    dept1 = SysDepartment(dept_name="设备管理部", dept_code="EQM", sort_order=1)
    dept2 = SysDepartment(dept_name="施工一队", dept_code="C01", sort_order=2)
    dept3 = SysDepartment(dept_name="施工二队", dept_code="C02", sort_order=3)
    db.add_all([dept1, dept2, dept3])
    db.flush()

    # ============ 用户 ============
    users = [
        SysUser(username="admin", password_hash=hash_password("admin123"), real_name="系统管理员", phone="13800000001", role_id=admin_role.id, department_id=dept1.id, status=1),
        SysUser(username="manager", password_hash=hash_password("manager123"), real_name="张主管", phone="13800000002", role_id=manager_role.id, department_id=dept1.id, status=1),
        SysUser(username="operator01", password_hash=hash_password("123456"), real_name="李操作", phone="13800000003", role_id=operator_role.id, department_id=dept2.id, status=1),
        SysUser(username="driver01", password_hash=hash_password("123456"), real_name="王驾驶员", phone="13800000004", role_id=driver_role.id, department_id=dept2.id, status=1),
    ]
    db.add_all(users)
    db.flush()

    # ============ 设备类别 ============
    cat_excavator = EquipmentCategory(category_name="挖掘机", category_code="EXC", is_special_default=0, sort_order=1)
    cat_loader = EquipmentCategory(category_name="装载机", category_code="LOD", is_special_default=0, sort_order=2)
    cat_crane = EquipmentCategory(category_name="龙门吊", category_code="GANTRY", is_special_default=1, sort_order=3)
    cat_bridge = EquipmentCategory(category_name="架桥机", category_code="BRG", is_special_default=1, sort_order=4)
    cat_crawler = EquipmentCategory(category_name="履带式起重机", category_code="CRC", is_special_default=1, sort_order=5)
    cat_roller = EquipmentCategory(category_name="压路机", category_code="ROL", is_special_default=0, sort_order=6)
    db.add_all([cat_excavator, cat_loader, cat_crane, cat_bridge, cat_crawler, cat_roller])
    db.flush()

    # ============ 扩展字段定义 ============
    field_defs = [
        EquipmentFieldDef(field_key="engine_power", field_label="发动机功率(kW)", field_type="number", category_id=cat_excavator.id, is_required=0),
        EquipmentFieldDef(field_key="bucket_capacity", field_label="斗容(m³)", field_type="number", category_id=cat_excavator.id, is_required=0),
        EquipmentFieldDef(field_key="rated_load", field_label="额定起重量(t)", field_type="number", category_id=cat_crane.id, is_required=1),
        EquipmentFieldDef(field_key="span", field_label="跨度(m)", field_type="number", category_id=cat_crane.id, is_required=0),
        EquipmentFieldDef(field_key="lifting_height", field_label="起升高度(m)", field_type="number", category_id=cat_crane.id, is_required=0),
        # 全局字段
        EquipmentFieldDef(field_key="ownership", field_label="设备归属", field_type="select", field_options='[{"label":"自有","value":"self"},{"label":"租赁","value":"rent"}]', category_id=None, is_required=0),
    ]
    db.add_all(field_defs)
    db.flush()

    # ============ 项目 ============
    project = Project(project_name="地铁10号线施工项目", project_code="M10", location="市区", start_date=date(2024, 3, 1), end_date=date(2025, 12, 31), status=1, manager_name="张主管")
    db.add(project)
    db.flush()

    # ============ 设备 ============
    def create_eq(code, name, model, brand, cat_id, is_special, location, driver, phone, put_use, hours, photo=None, extra=None):
        token = generate_qr_token()
        eq = Equipment(
            equipment_code=code, qr_token=token, name=name, model=model, brand=brand,
            category_id=cat_id, is_special=is_special, status=1, photo_url=photo,
            put_use_date=put_use, location=location, project_id=project.id,
            driver_name=driver, driver_phone=phone,
            total_running_hours=Decimal(str(hours)),
            last_maintain_date=date.today() - timedelta(days=80),
            last_maintain_hours=Decimal(str(max(hours - 240, 0))),
            extra_attributes=extra or {},
        )
        db.add(eq)
        db.flush()
        # 生成二维码图片
        generate_qr_code(code, token)
        return eq

    eq1 = create_eq("EXC-001", "小松PC200挖掘机", "PC200-8", "小松", cat_excavator.id, 0, "1号工地", "王驾驶员", "13800000004", date(2022, 5, 1), 3200, extra={"engine_power": 103, "bucket_capacity": 0.8, "ownership": "self"})
    eq2 = create_eq("LOD-001", "柳工855N装载机", "855N", "柳工", cat_loader.id, 0, "1号工地", "李操作", "13800000003", date(2021, 8, 15), 2800, extra={"engine_power": 162, "ownership": "self"})
    eq3 = create_eq("GANTRY-001", "20t龙门吊", "MH20-30", "中原", cat_crane.id, 1, "2号工地", "刘司机", "13800000005", date(2023, 3, 1), 1500, extra={"rated_load": 20, "span": 30, "lifting_height": 12})
    eq4 = create_eq("BRG-001", "160t架桥机", "JQ160", "武桥", cat_bridge.id, 1, "3号工地", "陈司机", "13800000006", date(2023, 6, 1), 800, extra={"rated_load": 160})
    eq5 = create_eq("CRC-001", "150t履带式起重机", "QUY150", "徐工", cat_crawler.id, 1, "2号工地", "赵司机", "13800000007", date(2022, 10, 1), 2200, extra={"rated_load": 150})
    eq6 = create_eq("ROL-001", "三一STR130压路机", "STR130", "三一", cat_roller.id, 0, "1号工地", "孙司机", "13800000008", date(2024, 1, 10), 320, extra={"ownership": "rent"})
    db.flush()

    # ============ 保险 ============
    ins1 = EquipmentInsurance(equipment_id=eq1.id, insurance_type="工程一切险", insurance_company="中国人保", policy_number="PA20240001", premium=Decimal("8000"), start_date=date(2024, 1, 1), end_date=date(2025, 6, 30), status=1)
    ins2 = EquipmentInsurance(equipment_id=eq3.id, insurance_type="特种设备责任险", insurance_company="平安保险", policy_number="PA20240002", premium=Decimal("15000"), start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), status=1)
    db.add_all([ins1, ins2])

    # ============ 特种设备扩展 ============
    special_exts = [
        SpecialEquipmentExt(
            equipment_id=eq3.id, registration_number="TS-GANTRY-2023001", registration_date=date(2023, 3, 1), registration_expiry=date(2027, 3, 1),
            inspection_type="定检", last_inspection_date=date(2024, 3, 1), next_inspection_date=date.today() + timedelta(days=20), inspection_status=1,
            operator_name="刘司机", operator_cert_number="TSG-CRANE-001", operator_cert_expiry=date.today() + timedelta(days=50),
            install_dismantle_plan_url="/uploads/special/plan_gantry.pdf", install_dismantle_plan_date=date(2023, 2, 20),
            acceptance_record_url="/uploads/special/accept_gantry.pdf", acceptance_date=date(2023, 3, 5), acceptance_status=1,
            supervision_agency="市特种设备监督检验所", compliance_status=2,
        ),
        SpecialEquipmentExt(
            equipment_id=eq4.id, registration_number="TS-BRG-2023002", registration_date=date(2023, 6, 1), registration_expiry=date(2027, 6, 1),
            inspection_type="首检", last_inspection_date=date(2023, 6, 10), next_inspection_date=date.today() + timedelta(days=120), inspection_status=1,
            operator_name="陈司机", operator_cert_number="TSG-BRG-002", operator_cert_expiry=date.today() - timedelta(days=5),  # 已过期，用于演示
            install_dismantle_plan_url="/uploads/special/plan_bridge.pdf", install_dismantle_plan_date=date(2023, 5, 20),
            acceptance_record_url="/uploads/special/accept_bridge.pdf", acceptance_date=date(2023, 6, 5), acceptance_status=1,
            supervision_agency="市特种设备监督检验所", compliance_status=3,
        ),
        SpecialEquipmentExt(
            equipment_id=eq5.id, registration_number="TS-CRC-2023003", registration_date=date(2022, 10, 1), registration_expiry=date(2026, 10, 1),
            inspection_type="定检", last_inspection_date=date(2024, 4, 1), next_inspection_date=date.today() + timedelta(days=200), inspection_status=1,
            operator_name="赵司机", operator_cert_number="TSG-CRC-003", operator_cert_expiry=date.today() + timedelta(days=300),
            install_dismantle_plan_url="/uploads/special/plan_crawler.pdf", install_dismantle_plan_date=date(2022, 9, 20),
            acceptance_record_url="/uploads/special/accept_crawler.pdf", acceptance_date=date(2022, 10, 5), acceptance_status=1,
            supervision_agency="省特种设备检验院", compliance_status=1,
        ),
    ]
    db.add_all(special_exts)

    # ============ 维保计划 ============
    plans = [
        MaintenancePlan(equipment_id=eq1.id, plan_name="每250小时定期保养", maintain_type="periodic", trigger_type=3, trigger_hours=Decimal("250"), trigger_days=90, advance_notify_days=7, advance_notify_hours=Decimal("20")),
        MaintenancePlan(equipment_id=eq2.id, plan_name="每300小时定期保养", maintain_type="periodic", trigger_type=1, trigger_hours=Decimal("300"), advance_notify_hours=Decimal("25")),
        MaintenancePlan(equipment_id=eq3.id, plan_name="龙门吊季度维保", maintain_type="periodic", trigger_type=2, trigger_days=90, advance_notify_days=15),
        MaintenancePlan(equipment_id=eq5.id, plan_name="每500小时大保", maintain_type="major", trigger_type=3, trigger_hours=Decimal("500"), trigger_days=180, advance_notify_days=10, advance_notify_hours=Decimal("30")),
    ]
    db.add_all(plans)

    # ============ 维保记录 ============
    records = [
        MaintenanceRecord(equipment_id=eq1.id, plan_id=plans[0].id, maintain_type="periodic", maintain_date=date.today() - timedelta(days=80), running_hours=Decimal("2960"), cost=Decimal("1500"), parts_replaced="机油滤芯、柴油滤芯", maintainer="设备部", description="更换三滤，检查液压系统", result=1, next_maintain_date=date.today() + timedelta(days=10), next_maintain_hours=Decimal("3210")),
        MaintenanceRecord(equipment_id=eq3.id, plan_id=plans[2].id, maintain_type="periodic", maintain_date=date.today() - timedelta(days=85), running_hours=Decimal("1450"), cost=Decimal("3000"), parts_replaced="钢丝绳润滑", maintainer="维保厂家", description="润滑保养，检查钢结构", result=1, next_maintain_date=date.today() + timedelta(days=5)),
    ]
    db.add_all(records)

    # ============ 加油记录 ============
    fuel_records = [
        FuelRecord(equipment_id=eq1.id, fuel_date=datetime.now() - timedelta(days=10), fuel_type="0#柴油", volume=Decimal("150"), unit_price=Decimal("7.5"), total_amount=Decimal("1125"), running_hours=Decimal("3180"), previous_hours=Decimal("3050"), fuel_consumption=Decimal("11.5"), operator_name="王驾驶员", refueling_station="中石化1号站", source=1),
        FuelRecord(equipment_id=eq1.id, fuel_date=datetime.now() - timedelta(days=5), fuel_type="0#柴油", volume=Decimal("130"), unit_price=Decimal("7.6"), total_amount=Decimal("988"), running_hours=Decimal("3200"), previous_hours=Decimal("3180"), fuel_consumption=Decimal("6.5"), operator_name="王驾驶员", refueling_station="中石化1号站", source=1),
        FuelRecord(equipment_id=eq2.id, fuel_date=datetime.now() - timedelta(days=7), fuel_type="0#柴油", volume=Decimal("200"), unit_price=Decimal("7.5"), total_amount=Decimal("1500"), running_hours=Decimal("2790"), previous_hours=Decimal("2640"), fuel_consumption=Decimal("13.3"), operator_name="李操作", refueling_station="中石油2号站", source=1),
    ]
    db.add_all(fuel_records)

    # ============ 运转记录 ============
    op_logs = [
        OperationLog(equipment_id=eq1.id, log_date=date.today(), shift=1, start_hours=Decimal("3195"), end_hours=Decimal("3200"), running_hours=Decimal("5"), work_content="基坑开挖", work_location="1号工地", operator_name="王驾驶员", handover_status=1, equipment_condition="正常", safety_check=1),
        OperationLog(equipment_id=eq2.id, log_date=date.today(), shift=1, start_hours=Decimal("2780"), end_hours=Decimal("2790"), running_hours=Decimal("10"), work_content="装车作业", work_location="1号工地", operator_name="李操作", handover_status=0, equipment_condition="正常", safety_check=1),
    ]
    db.add_all(op_logs)

    # ============ 报修 ============
    repair1 = RepairRequest(request_no="WX20240101ABCD", equipment_id=eq2.id, reporter_name="李操作", reporter_phone="13800000003", fault_type="液压", fault_level=2, fault_description="液压油缸漏油，举升无力", status=2, approved_at=datetime.now() - timedelta(days=2), repairer="设备部", repair_start=datetime.now() - timedelta(days=1))
    db.add(repair1)

    # ============ 培训 ============
    training1 = TrainingPlan(plan_name="挖掘机安全操作培训", training_type="安全操作", target_audience="全体挖掘机驾驶员", planned_date=datetime.now() + timedelta(days=7), duration_hours=Decimal("4"), instructor="张主管", location="项目部会议室", content_summary="挖掘机安全操作规程、应急处置", status=1, material_urls='["/uploads/training/m1.pdf"]')
    training2 = TrainingPlan(plan_name="特种设备作业人员复审培训", training_type="特种作业", target_audience="龙门吊、架桥机操作人员", planned_date=datetime.now() - timedelta(days=30), actual_date=datetime.now() - timedelta(days=30), duration_hours=Decimal("8"), instructor="外聘专家", location="市特检所", content_summary="特种设备法规、操作证复审", status=2)
    db.add_all([training1, training2])
    db.flush()

    participants = [
        TrainingParticipant(training_id=training2.id, user_name="王驾驶员", attendance=1, exam_score=Decimal("88"), exam_passed=1),
        TrainingParticipant(training_id=training2.id, user_name="刘司机", attendance=1, exam_score=Decimal("92"), exam_passed=1),
        TrainingParticipant(training_id=training2.id, user_name="陈司机", attendance=0, exam_score=None, exam_passed=None),
    ]
    db.add_all(participants)

    # ============ 维保提醒（演示） ============
    reminder1 = MaintenanceReminder(equipment_id=eq3.id, plan_id=plans[2].id, reminder_type=2, target_date=date.today() + timedelta(days=5), status=1, notified_at=datetime.now())
    db.add(reminder1)

    db.commit()
    print("[初始化] 示例数据填充完成！")
    print("[初始化] 管理员账号: admin / admin123")
    print("[初始化] 主管账号: manager / manager123")
    print("[初始化] 操作员账号: operator01 / 123456")
