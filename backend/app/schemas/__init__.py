from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


# ---------- common ----------
class ResponseModel(BaseModel):
    code: int = 0
    msg: str = "ok"
    data: Optional[Union[dict, list]] = None


# ---------- auth ----------
class RegisterIn(BaseModel):
    student_id: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=64)
    real_name: str = Field("", max_length=64)


class LoginIn(BaseModel):
    student_id: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    student_id: str
    real_name: str
    role: str
    avatar: str
    bio: str

    class Config:
        from_attributes = True


class UserUpdateIn(BaseModel):
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


# ---------- hollow ----------
class HollowPostIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    mood_tag: str = ""
    is_anonymous: bool = True


class HollowReplyIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: int = 0
    is_anonymous: bool = True


class HollowReplyOut(BaseModel):
    id: int
    post_id: int
    parent_id: int
    content: str
    nickname: str
    avatar: str
    is_mine: bool
    like_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class HollowPostOut(BaseModel):
    id: int
    content: str
    mood_tag: str
    nickname: str
    avatar: str
    is_mine: bool
    like_count: int
    reply_count: int
    is_liked: bool = False
    is_crisis: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportIn(BaseModel):
    target_type: str
    target_id: int
    reason: str


# ---------- content ----------
class ArticleOut(BaseModel):
    id: int
    title: str
    category: str
    content_type: str
    cover: str
    summary: str
    content: str
    video_url: str
    author: str
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleIn(BaseModel):
    title: str
    category: str
    content_type: str = "article"
    cover: str = ""
    summary: str = ""
    content: str = ""
    video_url: str = ""
    author: str = "树洞编辑部"
    is_published: bool = True


class MoodIn(BaseModel):
    mood: str
    score: int = Field(3, ge=1, le=5)
    note: str = ""
    record_date: Optional[date] = None


class MoodOut(BaseModel):
    id: int
    record_date: date
    mood: str
    score: int
    note: str
    created_at: datetime

    class Config:
        from_attributes = True


class BreathingIn(BaseModel):
    duration_seconds: int
    cycles: int


# ---------- group ----------
class GroupIn(BaseModel):
    name: str
    topic: str
    description: str = ""
    cover: str = ""


class GroupOut(BaseModel):
    id: int
    name: str
    topic: str
    description: str
    cover: str
    member_count: int
    is_active: bool
    is_joined: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityIn(BaseModel):
    group_id: int
    title: str
    description: str = ""
    location: str = "线上"
    start_time: datetime
    end_time: datetime
    capacity: int = 20


class ActivityOut(BaseModel):
    id: int
    group_id: int
    group_name: str = ""
    title: str
    description: str
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int
    enrolled_count: int
    status: str
    is_enrolled: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- appointment ----------
class CounselorOut(BaseModel):
    id: int
    name: str
    title: str
    avatar: str
    expertise: str
    introduction: str
    available_slots: list = []
    rating: int

    class Config:
        from_attributes = True


class CounselorIn(BaseModel):
    user_id: int
    name: str
    title: str = "校园心理老师"
    avatar: str = ""
    expertise: str = ""
    introduction: str = ""
    available_slots: list = []


class AppointmentIn(BaseModel):
    counselor_id: int
    appointment_time: datetime
    duration_minutes: int = 50
    topic: str = ""
    description: str = ""
    contact: str = ""


class AppointmentOut(BaseModel):
    id: int
    user_id: int
    counselor_id: int
    counselor_name: str = ""
    student_name: str = ""
    appointment_time: datetime
    duration_minutes: int
    topic: str
    description: str
    contact: str
    status: str
    counselor_note: str
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentStatusIn(BaseModel):
    status: str
    counselor_note: str = ""


# ---------- notification ----------
class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    content: str
    link: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- ai ----------
class AiSessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AiMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AiChatIn(BaseModel):
    session_id: Optional[int] = None
    content: str
    use_rag: bool = True
    file_ids: Optional[List[int]] = None


# ---------- knowledge ----------
class KnowledgeFileOut(BaseModel):
    id: int
    filename: str
    mime_type: str
    size_bytes: int
    chunk_count: int
    is_enabled: bool
    status: str
    error_msg: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSearchHit(BaseModel):
    file_id: int
    filename: str = ""
    text: str
    score: float


TokenOut.model_rebuild()
