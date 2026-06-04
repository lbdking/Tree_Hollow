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

    def mood_distribution(self, db: Session, age_group: str = None) -> List[dict]:
        """
        获取心情分布，支持按年龄段筛选
        
        :param age_group: 年龄段筛选，可选值: None(全部), 'under18', '18-20', '21-23', 'over24'
        """
        # 根据学号推断年龄的辅助函数
        def get_age_group(student_id: str) -> str:
            # 学号格式: 2024001 → 入学年份 2024
            if not student_id or len(student_id) < 4:
                return "unknown"
            try:
                year = int(student_id[:4])
                current_year = datetime.now().year
                grade = current_year - year  # 年级
                age = grade + 18  # 假设入学年龄为18岁
                if age < 18:
                    return "under18"
                elif 18 <= age <= 20:
                    return "18-20"
                elif 21 <= age <= 23:
                    return "21-23"
                else:
                    return "over24"
            except:
                return "unknown"
        
        # 查询心情记录和用户信息
        query = db.query(MoodRecord.mood, User.student_id).join(User, MoodRecord.user_id == User.id)
        
        if age_group and age_group != "all":
            # 先获取该年龄段的用户ID
            age_users = {}
            all_users = db.query(User.id, User.student_id).filter(User.is_deleted == False).all()
            for user_id, student_id in all_users:
                if get_age_group(student_id) == age_group:
                    age_users[user_id] = True
            
            if age_users:
                query = query.filter(MoodRecord.user_id.in_(age_users.keys()))
            else:
                return []
        
        all_moods = query.all()
        mood_counts = {}
        for mood, _ in all_moods:
            if mood in mood_counts:
                mood_counts[mood] += 1
            else:
                mood_counts[mood] = 1
        
        total = sum(mood_counts.values())
        result = []
        for mood, count in mood_counts.items():
            percentage = round((count / total) * 100, 1) if total > 0 else 0
            result.append({
                "mood": mood,
                "count": count,
                "percentage": percentage
            })
        
        return result

    def get_age_groups(self, db: Session) -> List[dict]:
        """获取所有年龄段分布统计"""
        def get_age_group(student_id: str) -> str:
            if not student_id or len(student_id) < 4:
                return "unknown"
            try:
                year = int(student_id[:4])
                current_year = datetime.now().year
                grade = current_year - year
                age = grade + 18
                if age < 18:
                    return "under18"
                elif 18 <= age <= 20:
                    return "18-20"
                elif 21 <= age <= 23:
                    return "21-23"
                else:
                    return "over24"
            except:
                return "unknown"
        
        all_users = db.query(User.student_id).filter(User.is_deleted == False).all()
        age_counts = {
            "under18": 0,
            "18-20": 0,
            "21-23": 0,
            "over24": 0,
            "unknown": 0
        }
        
        for (student_id,) in all_users:
            group = get_age_group(student_id)
            age_counts[group] += 1
        
        return [
            {"group": "18岁以下", "key": "under18", "count": age_counts["under18"]},
            {"group": "18-20岁", "key": "18-20", "count": age_counts["18-20"]},
            {"group": "21-23岁", "key": "21-23", "count": age_counts["21-23"]},
            {"group": "24岁以上", "key": "over24", "count": age_counts["over24"]},
        ]


stats = CRUDStats()
