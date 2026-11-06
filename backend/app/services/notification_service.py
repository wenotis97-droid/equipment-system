"""通知服务"""
from sqlalchemy.orm import Session
from app.models.misc import Notification


def list_notifications(db: Session, user_id: int, is_read: int = None, page: int = 1, page_size: int = 20) -> dict:
    q = db.query(Notification).filter(Notification.user_id == user_id)
    if is_read is not None:
        q = q.filter(Notification.is_read == is_read)
    total = q.count()
    items = q.order_by(Notification.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [{
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "type": n.type,
            "ref_type": n.ref_type,
            "ref_id": n.ref_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        } for n in items],
    }


def mark_read(db: Session, notification_id: int) -> bool:
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        return False
    n.is_read = 1
    db.commit()
    return True


def mark_all_read(db: Session, user_id: int) -> int:
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == 0,
    ).update({Notification.is_read: 1})
    db.commit()
    return count


def unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == 0,
    ).count()
