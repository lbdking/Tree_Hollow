from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.content import Article, BreathingRecord, MoodRecord


class CRUDArticle(CRUDBase[Article, dict, dict]):
    def list_published(
        self,
        db: Session,
        *,
        page: int = 1,
        size: int = 10,
        category: Optional[str] = None,
        content_type: Optional[str] = None,
    ):
        q = db.query(Article).filter(Article.is_published == True)
        if category:
            q = q.filter(Article.category == category)
        if content_type:
            q = q.filter(Article.content_type == content_type)
        total = q.count()
        items = q.order_by(desc(Article.created_at)).offset((page - 1) * size).limit(size).all()
        return total, items

    def incr_view(self, db: Session, article: Article):
        article.view_count += 1
        db.commit()


class CRUDMood(CRUDBase[MoodRecord, dict, dict]):
    def upsert(
        self, db: Session, *, user_id: int, record_date: date, mood: str, score: int, note: str
    ) -> MoodRecord:
        existing = (
            db.query(MoodRecord)
            .filter(MoodRecord.user_id == user_id, MoodRecord.record_date == record_date)
            .first()
        )
        if existing:
            existing.mood = mood
            existing.score = score
            existing.note = note
            db.commit()
            db.refresh(existing)
            return existing
        m = MoodRecord(user_id=user_id, record_date=record_date, mood=mood, score=score, note=note)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m

    def list_by_month(
        self, db: Session, *, user_id: int, year: Optional[int] = None, month: Optional[int] = None
    ) -> List[MoodRecord]:
        q = db.query(MoodRecord).filter(MoodRecord.user_id == user_id)
        if year and month:
            from calendar import monthrange
            last = monthrange(year, month)[1]
            q = q.filter(MoodRecord.record_date >= date(year, month, 1))
            q = q.filter(MoodRecord.record_date <= date(year, month, last))
        elif year:
            q = q.filter(MoodRecord.record_date >= date(year, 1, 1))
        return q.order_by(MoodRecord.record_date.asc()).all()


class CRUDBreathing(CRUDBase[BreathingRecord, dict, dict]):
    def stats(self, db: Session, user_id: int):
        items = db.query(BreathingRecord).filter(BreathingRecord.user_id == user_id).all()
        return {
            "count": len(items),
            "total_seconds": sum(i.duration_seconds for i in items),
            "total_cycles": sum(i.cycles for i in items),
        }


article = CRUDArticle(Article)
mood = CRUDMood(MoodRecord)
breathing = CRUDBreathing(BreathingRecord)
