"""安全培训服务"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.training import TrainingPlan, TrainingParticipant
from app.schemas.business import TrainingPlanCreate, TrainingParticipantCreate


def list_training_plans(db: Session, status: int = None, page: int = 1, page_size: int = 20) -> dict:
    q = db.query(TrainingPlan)
    if status is not None:
        q = q.filter(TrainingPlan.status == status)
    total = q.count()
    items = q.order_by(TrainingPlan.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for p in items:
        participant_count = db.query(TrainingParticipant).filter(TrainingParticipant.training_id == p.id).count()
        result.append({
            "id": p.id,
            "plan_name": p.plan_name,
            "training_type": p.training_type,
            "target_audience": p.target_audience,
            "planned_date": p.planned_date.isoformat() if p.planned_date else None,
            "actual_date": p.actual_date.isoformat() if p.actual_date else None,
            "duration_hours": float(p.duration_hours) if p.duration_hours else None,
            "instructor": p.instructor,
            "location": p.location,
            "content_summary": p.content_summary,
            "material_urls": p.material_urls,
            "status": p.status,
            "participant_count": participant_count,
        })
    return {"total": total, "page": page, "page_size": page_size, "list": result}


def get_training_plan(db: Session, plan_id: int) -> Optional[dict]:
    p = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not p:
        return None
    participants = db.query(TrainingParticipant).filter(TrainingParticipant.training_id == plan_id).all()
    return {
        "id": p.id,
        "plan_name": p.plan_name,
        "training_type": p.training_type,
        "target_audience": p.target_audience,
        "planned_date": p.planned_date.isoformat() if p.planned_date else None,
        "actual_date": p.actual_date.isoformat() if p.actual_date else None,
        "duration_hours": float(p.duration_hours) if p.duration_hours else None,
        "instructor": p.instructor,
        "location": p.location,
        "content_summary": p.content_summary,
        "material_urls": p.material_urls,
        "status": p.status,
        "participants": [{
            "id": pt.id,
            "user_name": pt.user_name,
            "attendance": pt.attendance,
            "exam_score": float(pt.exam_score) if pt.exam_score else None,
            "exam_passed": pt.exam_passed,
            "certificate_url": pt.certificate_url,
            "remark": pt.remark,
        } for pt in participants],
    }


def create_training_plan(db: Session, req: TrainingPlanCreate) -> TrainingPlan:
    plan = TrainingPlan(**req.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_training_plan(db: Session, plan_id: int, req: dict) -> Optional[TrainingPlan]:
    p = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    if not p:
        return None
    for k, v in req.items():
        if hasattr(p, k):
            setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


def add_participant(db: Session, req: TrainingParticipantCreate) -> TrainingParticipant:
    pt = TrainingParticipant(**req.model_dump())
    db.add(pt)
    db.commit()
    db.refresh(pt)
    return pt


def update_participant(db: Session, pt_id: int, req: dict) -> Optional[TrainingParticipant]:
    pt = db.query(TrainingParticipant).filter(TrainingParticipant.id == pt_id).first()
    if not pt:
        return None
    for k, v in req.items():
        if hasattr(pt, k):
            setattr(pt, k, v)
    db.commit()
    db.refresh(pt)
    return pt
