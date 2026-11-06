"""后台管理路由汇总"""
from fastapi import APIRouter
from app.routers.admin.auth import router as auth_router
from app.routers.admin.users import router as users_router
from app.routers.admin.equipment import router as equipment_router
from app.routers.admin.special_equipment import router as special_router
from app.routers.admin.maintenance import router as maintenance_router
from app.routers.admin.business import (
    fuel_router, operation_router, repair_router, training_router,
    statistics_router, project_router, notification_router,
)

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(auth_router)
admin_router.include_router(users_router)
admin_router.include_router(equipment_router)
admin_router.include_router(special_router)
admin_router.include_router(maintenance_router)
admin_router.include_router(fuel_router)
admin_router.include_router(operation_router)
admin_router.include_router(repair_router)
admin_router.include_router(training_router)
admin_router.include_router(statistics_router)
admin_router.include_router(project_router)
admin_router.include_router(notification_router)
