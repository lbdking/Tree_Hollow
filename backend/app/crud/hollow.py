from __future__ import annotations

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.hollow import HollowLike, HollowPost, HollowReply, Report


class CRUDHollowPost(CRUDBase[HollowPost, dict, dict]):
    def list_published(
        self,
        db: Session,
        *,
        page: int = 1,
        size: int = 10,
        mood_tag: Optional[str] = None,
        keyword: Optional[str] = None,
    ):
        q = db.query(HollowPost).filter(HollowPost.status == "published")
        if mood_tag:
            q = q.filter(HollowPost.mood_tag == mood_tag)
        if keyword:
            q = q.filter(HollowPost.content.like(f"%{keyword}%"))
        total = q.count()
        items = q.order_by(desc(HollowPost.created_at)).offset((page - 1) * size).limit(size).all()
        return total, items

    def list_my(self, db: Session, user_id: int) -> List[HollowPost]:
        return (
            db.query(HollowPost)
            .filter(HollowPost.user_id == user_id, HollowPost.status != "deleted")
            .order_by(desc(HollowPost.created_at))
            .all()
        )

    def list_admin(self, db: Session, page: int, size: int):
        q = db.query(HollowPost).order_by(desc(HollowPost.created_at))
        total = q.count()
        items = q.offset((page - 1) * size).limit(size).all()
        return total, items

    def set_status(self, db: Session, post: HollowPost, status: str) -> HollowPost:
        post.status = status
        db.commit()
        db.refresh(post)
        return post

    def incr_reply_count(self, db: Session, post: HollowPost, delta: int = 1):
        post.reply_count += delta
        db.commit()

    def adjust_like(self, db: Session, post: HollowPost, delta: int):
        post.like_count = max(0, post.like_count + delta)
        db.commit()


class CRUDHollowReply(CRUDBase[HollowReply, dict, dict]):
    def list_by_post(self, db: Session, post_id: int) -> List[HollowReply]:
        return (
            db.query(HollowReply)
            .filter(HollowReply.post_id == post_id, HollowReply.status == "published")
            .order_by(HollowReply.created_at.asc())
            .all()
        )

    def adjust_like(self, db: Session, reply: HollowReply, delta: int):
        reply.like_count = max(0, reply.like_count + delta)
        db.commit()

    def set_status(self, db: Session, reply: HollowReply, status: str):
        reply.status = status
        db.commit()


class CRUDLike(CRUDBase[HollowLike, dict, dict]):
    def find(self, db: Session, user_id: int, target_type: str, target_id: int) -> Optional[HollowLike]:
        return (
            db.query(HollowLike)
            .filter(
                HollowLike.user_id == user_id,
                HollowLike.target_type == target_type,
                HollowLike.target_id == target_id,
            )
            .first()
        )


class CRUDReport(CRUDBase[Report, dict, dict]):
    def list_by_status(self, db: Session, status: Optional[str] = None) -> List[Report]:
        q = db.query(Report)
        if status:
            q = q.filter(Report.status == status)
        return q.order_by(desc(Report.created_at)).all()

    def mark_handled(self, db: Session, report: Report, *, status: str, admin_id: int):
        from datetime import datetime
        report.status = status
        report.handled_by = admin_id
        report.handled_at = datetime.utcnow()
        db.commit()


hollow_post = CRUDHollowPost(HollowPost)
hollow_reply = CRUDHollowReply(HollowReply)
hollow_like = CRUDLike(HollowLike)
report = CRUDReport(Report)
