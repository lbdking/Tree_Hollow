from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Counselor(Base):
    __tablename__ = "counselor"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(64), default="校园心理老师")
    avatar: Mapped[str] = mapped_column(String(500), default="")
    expertise: Mapped[str] = mapped_column(String(255), default="", comment="擅长领域，逗号分隔")
    introduction: Mapped[str] = mapped_column(Text, default="")
    available_slots: Mapped[str] = mapped_column(Text, default="[]", comment="JSON: 可预约时段")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[int] = mapped_column(Integer, default=5, comment="评分 1~5")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True)
    counselor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("counselor.id"), index=True)
    appointment_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=50)
    topic: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    contact: Mapped[str] = mapped_column(String(64), default="", comment="联系方式（可匿名留空）")
    status: Mapped[str] = mapped_column(
        String(16),
        default="pending",
        comment="pending/confirmed/cancelled/completed/rejected",
    )
    counselor_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
