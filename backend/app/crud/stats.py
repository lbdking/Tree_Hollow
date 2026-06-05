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

    def _get_period_range(self, period: str):
        """获取周期对应的时间范围"""
        now = datetime.utcnow()
        if period == 'day':
            # 最近30天
            return now - timedelta(days=30), '%Y-%m-%d', 'day'
        elif period == 'week':
            # 最近12周
            return now - timedelta(weeks=12), '%Y-%m-%d', 'week'
        elif period == 'month':
            # 最近12个月
            return now - timedelta(days=365), '%Y-%m', 'month'
        else:
            return now - timedelta(days=30), '%Y-%m-%d', 'day'

    def _format_period(self, dt, period: str):
        """根据周期格式化日期"""
        # 处理可能的类型转换问题
        if hasattr(dt, 'date'):
            dt = dt.date()
        elif isinstance(dt, str):
            dt = datetime.strptime(dt, '%Y-%m-%d').date()
        
        if period == 'day':
            return dt.strftime('%Y-%m-%d')
        elif period == 'week':
            # 返回周起始日期（周一）
            monday = dt - timedelta(days=dt.weekday())
            return monday.strftime('%Y-%m-%d')
        elif period == 'month':
            return dt.strftime('%Y-%m')
        return dt.strftime('%Y-%m-%d')

    def get_posts_trend(self, db: Session, period: str = 'day') -> List[dict]:
        """
        获取发帖趋势
        :param period: day/week/month
        """
        since, fmt, _ = self._get_period_range(period)
        if period == 'week':
            # MySQL 按周统计，使用 YEARWEEK
            rows = (
                db.query(
                    func.yearweek(HollowPost.created_at).label("week_num"),
                    func.count().label("c")
                )
                .filter(HollowPost.created_at >= since)
                .group_by("week_num")
                .order_by("week_num")
                .all()
            )
            result = []
            for week_num, c in rows:
                # 将 YEARWEEK 格式转换为日期格式
                year = int(str(week_num)[:4])
                week = int(str(week_num)[4:])
                # 计算该周的周一日期
                first_day = datetime(year, 1, 1)
                if first_day.weekday() > 0:
                    first_day = first_day + timedelta(days=7 - first_day.weekday())
                else:
                    first_day = first_day - timedelta(days=first_day.weekday())
                monday = first_day + timedelta(weeks=week - 1)
                result.append({"date": monday.strftime('%Y-%m-%d'), "count": c})
            return result
        elif period == 'month':
            # MySQL 按月统计
            rows = (
                db.query(
                    func.date_format(HollowPost.created_at, '%Y-%m').label("month_str"),
                    func.count().label("c")
                )
                .filter(HollowPost.created_at >= since)
                .group_by("month_str")
                .order_by("month_str")
                .all()
            )
            result = []
            for month_str, c in rows:
                result.append({"date": month_str, "count": c})
            return result
        else:
            # 按日统计
            rows = (
                db.query(func.date(HollowPost.created_at).label("d"), func.count().label("c"))
                .filter(HollowPost.created_at >= since)
                .group_by("d")
                .order_by("d")
                .all()
            )
            return [{"date": str(d), "count": c} for d, c in rows]

    def get_users_trend(self, db: Session, period: str = 'day') -> List[dict]:
        """
        获取用户注册增长趋势
        :param period: day/week/month
        """
        since, fmt, _ = self._get_period_range(period)
        if period == 'week':
            # MySQL 按周统计
            rows = (
                db.query(
                    func.yearweek(User.created_at).label("week_num"),
                    func.count().label("c")
                )
                .filter(User.created_at >= since, User.is_deleted == False)
                .group_by("week_num")
                .order_by("week_num")
                .all()
            )
            result = []
            for week_num, c in rows:
                year = int(str(week_num)[:4])
                week = int(str(week_num)[4:])
                first_day = datetime(year, 1, 1)
                if first_day.weekday() > 0:
                    first_day = first_day + timedelta(days=7 - first_day.weekday())
                else:
                    first_day = first_day - timedelta(days=first_day.weekday())
                monday = first_day + timedelta(weeks=week - 1)
                result.append({"date": monday.strftime('%Y-%m-%d'), "count": c})
            return result
        elif period == 'month':
            # MySQL 按月统计
            rows = (
                db.query(
                    func.date_format(User.created_at, '%Y-%m').label("month_str"),
                    func.count().label("c")
                )
                .filter(User.created_at >= since, User.is_deleted == False)
                .group_by("month_str")
                .order_by("month_str")
                .all()
            )
            result = []
            for month_str, c in rows:
                result.append({"date": month_str, "count": c})
            return result
        else:
            rows = (
                db.query(func.date(User.created_at).label("d"), func.count().label("c"))
                .filter(User.created_at >= since, User.is_deleted == False)
                .group_by("d")
                .order_by("d")
                .all()
            )
            return [{"date": str(d), "count": c} for d, c in rows]

    def mood_distribution(self, db: Session, age_group: str = None) -> List[dict]:
        """
        获取心情分布，支持按年龄段筛选
        
        :param age_group: 年龄段筛选，可选值: None(全部), 'under18', '18-20', '21-23', 'over24'
        """
        def get_age_group(age: int) -> str:
            if age is None:
                return "unknown"
            if age < 18:
                return "under18"
            elif 18 <= age <= 20:
                return "18-20"
            elif 21 <= age <= 23:
                return "21-23"
            else:
                return "over24"
        
        # 查询心情记录和用户信息
        query = db.query(MoodRecord.mood, User.age).join(User, MoodRecord.user_id == User.id)
        
        if age_group and age_group != "all":
            # 先获取该年龄段的用户ID
            age_users = {}
            all_users = db.query(User.id, User.age).filter(User.is_deleted == False).all()
            for user_id, age in all_users:
                if get_age_group(age) == age_group:
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
        def get_age_group(age: int) -> str:
            if age is None:
                return "unknown"
            if age < 18:
                return "under18"
            elif 18 <= age <= 20:
                return "18-20"
            elif 21 <= age <= 23:
                return "21-23"
            else:
                return "over24"
        
        all_users = db.query(User.age).filter(User.is_deleted == False).all()
        age_counts = {
            "under18": 0,
            "18-20": 0,
            "21-23": 0,
            "over24": 0,
            "unknown": 0
        }
        
        for (age,) in all_users:
            group = get_age_group(age)
            age_counts[group] += 1
        
        return [
            {"group": "18岁以下", "key": "under18", "count": age_counts["under18"]},
            {"group": "18-20岁", "key": "18-20", "count": age_counts["18-20"]},
            {"group": "21-23岁", "key": "21-23", "count": age_counts["21-23"]},
            {"group": "24岁以上", "key": "over24", "count": age_counts["over24"]},
        ]


stats = CRUDStats()
