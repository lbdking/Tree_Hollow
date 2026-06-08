from __future__ import annotations

from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.notification import Notification


class CRUDNotification(CRUDBase[Notification, dict, dict]):
    def list_for_user(self, db: Session, user_id: int, page: int = 1, size: int = 20):
        q = db.query(Notification).filter(Notification.user_id == user_id).order_by(desc(Notification.created_at))
        total = q.count()
        items = q.offset((page - 1) * size).limit(size).all()
        return total, items

    def unread_count(self, db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    def mark_read(self, db: Session, notification: Notification):
        notification.is_read = True
        db.commit()

    def mark_all_read(self, db: Session, user_id: int):
        db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read == False
        ).update({"is_read": True})
        db.commit()

    def push(
        self, db: Session, *, user_id: int, type: str, title: str, content: str = "", link: str = ""
    ) -> Notification:
        n = Notification(user_id=user_id, type=type, title=title, content=content, link=link)
        db.add(n)
        db.commit()
        db.refresh(n)
        return n


notification = CRUDNotification(Notification)
