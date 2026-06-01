from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SupportGroup(Base):
    __tablename__ = "support_group"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    topic: Mapped[str] = mapped_column(String(64), index=True, comment="主题: 学业/恋爱/家庭/失眠/...")
    description: Mapped[str] = mapped_column(Text, default="")
    cover: Mapped[str] = mapped_column(String(500), default="")
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GroupMember(Base):
    __tablename__ = "group_member"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("support_group.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    role: Mapped[str] = mapped_column(String(16), default="member", comment="owner/admin/member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GroupActivity(Base):
    __tablename__ = "group_activity"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("support_group.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(255), default="线上")
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    capacity: Mapped[int] = mapped_column(Integer, default=20)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="open", comment="open/closed/finished")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ActivityEnrollment(Base):
    __tablename__ = "activity_enrollment"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    activity_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("group_activity.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="enrolled", comment="enrolled/cancelled")
    note: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
