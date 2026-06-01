from datetime import datetime, date

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(32), index=True, comment="如: 焦虑/抑郁/压力/睡眠/学业")
    content_type: Mapped[str] = mapped_column(String(16), default="article", comment="article/video")
    cover: Mapped[str] = mapped_column(String(500), default="")
    summary: Mapped[str] = mapped_column(String(500), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[str] = mapped_column(String(500), default="")
    author: Mapped[str] = mapped_column(String(64), default="树洞编辑部")
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MoodRecord(Base):
    __tablename__ = "mood_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    record_date: Mapped[date] = mapped_column(Date, index=True)
    mood: Mapped[str] = mapped_column(String(32), comment="emoji 或心情标签")
    score: Mapped[int] = mapped_column(Integer, default=3, comment="1~5 分")
    note: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BreathingRecord(Base):
    __tablename__ = "breathing_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    cycles: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
