from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.appointment import Appointment
from app.models.content import Article, MoodRecord
from app.models.group import SupportGroup
from app.models.hollow import HollowPost, HollowReply, Report
from app.models.user import User


class CRUDStats:
    """聚合统计数据访问。"""

    def summary(self, db: Session) -> Dict[str, int]:
        return {
            "user_total": db.query(User).filter(User.is_deleted == False).count(),
            "post_total": db.query(HollowPost).filter(HollowPost.status != "deleted").count(),
            "reply_total": db.query(HollowReply).filter(HollowReply.status != "deleted").count(),
            "crisis_total": db.query(HollowPost).filter(HollowPost.is_crisis == True).count(),
            "appointment_total": db.query(Appointment).count(),
            "article_total": db.query(Article).count(),
            "group_total": db.query(SupportGroup).count(),
            "pending_reports": db.query(Report).filter(Report.status == "pending").count(),
        }

    def posts_in_recent_days(self, db: Session, days: int = 7) -> List[dict]:
        since = datetime.utcnow() - timedelta(days=days)
        rows = (
            db.query(func.date(HollowPost.created_at).label("d"), func.count().label("c"))
            .filter(HollowPost.created_at >= since)
            .group_by("d")
            .all()
        )
        return [{"date": str(d), "count": c} for d, c in rows]

    def mood_distribution(self, db: Session) -> List[dict]:
        # 使用 Python 层面分组，避免 emoji 字符编码问题
        all_moods = db.query(MoodRecord.mood).all()
        mood_counts = {}
        for (mood,) in all_moods:
            if mood in mood_counts:
                mood_counts[mood] += 1
            else:
                mood_counts[mood] = 1
        return [{"mood": m, "count": c} for m, c in mood_counts.items()]


stats = CRUDStats()
