from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HollowPost(Base):
    __tablename__ = "hollow_post"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    mood_tag: Mapped[str] = mapped_column(String(32), default="", comment="心情标签")
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="published", comment="published/hidden/deleted")
    is_crisis: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否命中危机词")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HollowReply(Base):
    __tablename__ = "hollow_reply"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("hollow_post.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0, comment="父回复ID, 0=直接回帖")
    content: Mapped[str] = mapped_column(Text)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="published")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class HollowLike(Base):
    __tablename__ = "hollow_like"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(16), comment="post/reply")
    target_id: Mapped[int] = mapped_column(BigInteger, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "report"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    target_type: Mapped[str] = mapped_column(String(16), comment="post/reply")
    target_id: Mapped[int] = mapped_column(BigInteger)
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), default="pending", comment="pending/handled/rejected")
    handled_by: Mapped[int] = mapped_column(BigInteger, default=0)
    handled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
