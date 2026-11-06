"""加油记录、运转记录、报修、培训、统计、项目、通知路由（合并到一个文件便于管理）"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user_dep
from app.models.sys_user import SysUser
from app.models.misc import Project, Notification
from app.services.fuel_service import list_fuel_records, create_fuel_record, fuel_analysis
from app.services.operation_service import list_operation_logs
from app.services.repair_service import list_repairs, get_repair, action_repair
from app.services.training_service import list_training_plans, get_training_plan, create_training_plan, update_training_plan, add_participant, update_participant
from app.services.statistics_service import dashboard as dashboard_data
from app.services.notification_service import list_notifications, mark_read, mark_all_read, unread_count
from app.schemas.business import FuelRecordCreate, RepairActionRequest, TrainingPlanCreate, TrainingParticipantCreate
from app.schemas.sys import ProjectCreate
from app.schemas.common import ResponseBase

# 加油
fuel_router = APIRouter(prefix="/fuel", tags=["加油记录"])


@fuel_router.get("/records")
def fuel_list(equipment_id: int = None, page: int = 1, page_size: int = 20,
              start_date: str = None, end_date: str = None,
              db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_fuel_records(db, equipment_id, page, page_size, start_date, end_date))


@fuel_router.post("/records")
def fuel_create(req: FuelRecordCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    r = create_fuel_record(db, req, user.id)
    return ResponseBase.success({"id": r.id}, "添加成功")


@fuel_router.get("/analysis")
def fuel_analysis_api(equipment_id: int = None, start_date: str = None, end_date: str = None,
                      db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(fuel_analysis(db, equipment_id, start_date, end_date))


# 运转记录
operation_router = APIRouter(prefix="/operation", tags=["运转记录"])


@operation_router.get("/logs")
def operation_list(equipment_id: int = None, page: int = 1, page_size: int = 20,
                   start_date: str = None, end_date: str = None,
                   db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_operation_logs(db, equipment_id, page, page_size, start_date, end_date))


# 报修
repair_router = APIRouter(prefix="/repair", tags=["报修管理"])


@repair_router.get("/requests")
def repair_list(status: int = None, equipment_id: int = None, page: int = 1, page_size: int = 20,
                db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_repairs(db, status, equipment_id, page, page_size))


@repair_router.get("/requests/{repair_id}")
def repair_detail(repair_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    r = get_repair(db, repair_id)
    if not r:
        return ResponseBase.error("报修记录不存在")
    return ResponseBase.success(r)


@repair_router.put("/requests/{repair_id}/action")
def repair_action(repair_id: int, req: RepairActionRequest,
                  db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    r = action_repair(db, repair_id, req, user.id)
    if not r:
        return ResponseBase.error("报修记录不存在")
    return ResponseBase.success({"id": r.id, "status": r.status}, "操作成功")


# 培训
training_router = APIRouter(prefix="/training", tags=["安全培训"])


@training_router.get("/plans")
def training_list(status: int = None, page: int = 1, page_size: int = 20,
                  db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_training_plans(db, status, page, page_size))


@training_router.get("/plans/{plan_id}")
def training_detail(plan_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    p = get_training_plan(db, plan_id)
    if not p:
        return ResponseBase.error("培训计划不存在")
    return ResponseBase.success(p)


@training_router.post("/plans")
def training_create(req: TrainingPlanCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    p = create_training_plan(db, req)
    return ResponseBase.success({"id": p.id}, "创建成功")


@training_router.put("/plans/{plan_id}")
def training_update(plan_id: int, data: dict, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    p = update_training_plan(db, plan_id, data)
    if not p:
        return ResponseBase.error("培训计划不存在")
    return ResponseBase.success(message="更新成功")


@training_router.post("/plans/{plan_id}/participants")
def training_add_participant(plan_id: int, req: TrainingParticipantCreate,
                             db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    req.training_id = plan_id
    pt = add_participant(db, req)
    return ResponseBase.success({"id": pt.id}, "添加成功")


@training_router.put("/participants/{pt_id}")
def training_update_participant(pt_id: int, data: dict,
                               db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    pt = update_participant(db, pt_id, data)
    if not pt:
        return ResponseBase.error("参与记录不存在")
    return ResponseBase.success(message="更新成功")


# 统计
statistics_router = APIRouter(prefix="/statistics", tags=["统计分析"])


@statistics_router.get("/dashboard")
def dashboard_api(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(dashboard_data(db))


# 项目
project_router = APIRouter(prefix="/projects", tags=["项目管理"])


@project_router.get("")
def list_projects(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    items = db.query(Project).order_by(Project.id.desc()).all()
    return ResponseBase.success([{
        "id": p.id, "project_name": p.project_name, "project_code": p.project_code,
        "location": p.location, "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None, "status": p.status,
        "manager_name": p.manager_name,
    } for p in items])


@project_router.post("")
def create_project(req: ProjectCreate, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    p = Project(
        project_name=req.project_name, project_code=req.project_code,
        location=req.location, start_date=req.start_date, end_date=req.end_date,
        status=req.status, manager_name=req.manager_name,
    )
    db.add(p)
    db.commit()
    return ResponseBase.success({"id": p.id}, "创建成功")


# 通知
notification_router = APIRouter(prefix="/notifications", tags=["消息通知"])


@notification_router.get("")
def notification_list(is_read: int = None, page: int = 1, page_size: int = 20,
                      db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success(list_notifications(db, user.id, is_read, page, page_size))


@notification_router.put("/{notif_id}/read")
def notification_read(notif_id: int, db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    if not mark_read(db, notif_id):
        return ResponseBase.error("通知不存在")
    return ResponseBase.success(message="已标记已读")


@notification_router.put("/read-all")
def notification_read_all(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    count = mark_all_read(db, user.id)
    return ResponseBase.success({"count": count}, f"已标记{count}条为已读")


@notification_router.get("/unread-count")
def notification_unread(db: Session = Depends(get_db), user: SysUser = Depends(get_current_user_dep)):
    return ResponseBase.success({"count": unread_count(db, user.id)})
