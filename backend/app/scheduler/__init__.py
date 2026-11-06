"""定时任务：维保提醒 + 特种设备合规检查"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.database import SessionLocal
from app.services.maintenance_service import check_maintenance_by_calendar, check_maintenance_by_hours
from app.services.special_equipment_service import check_all_special_compliance

scheduler = AsyncIOScheduler()


def init_scheduler():
    """初始化定时任务"""
    # 每日凌晨 02:00 检查日历周期维保提醒
    scheduler.add_job(
        _job_check_calendar_maintenance,
        CronTrigger(hour=2, minute=0),
        id="check_calendar_maintenance",
        replace_existing=True,
    )

    # 每小时检查台时维保提醒
    scheduler.add_job(
        _job_check_hours_maintenance,
        IntervalTrigger(hours=1),
        id="check_hours_maintenance",
        replace_existing=True,
    )

    # 每日上午 08:30 检查特种设备合规状态
    scheduler.add_job(
        _job_check_compliance,
        CronTrigger(hour=8, minute=30),
        id="check_compliance",
        replace_existing=True,
    )

    scheduler.start()


def _job_check_calendar_maintenance():
    db = SessionLocal()
    try:
        count = check_maintenance_by_calendar(db)
        print(f"[定时任务] 日历维保检查完成，触发 {count} 条提醒")
    except Exception as e:
        print(f"[定时任务] 日历维保检查异常: {e}")
    finally:
        db.close()


def _job_check_hours_maintenance():
    db = SessionLocal()
    try:
        count = check_maintenance_by_hours(db)
        if count:
            print(f"[定时任务] 台时维保检查完成，触发 {count} 条提醒")
    except Exception as e:
        print(f"[定时任务] 台时维保检查异常: {e}")
    finally:
        db.close()


def _job_check_compliance():
    db = SessionLocal()
    try:
        count = check_all_special_compliance(db)
        print(f"[定时任务] 特种设备合规检查完成，共检查 {count} 台")
    except Exception as e:
        print(f"[定时任务] 特种设备合规检查异常: {e}")
    finally:
        db.close()
