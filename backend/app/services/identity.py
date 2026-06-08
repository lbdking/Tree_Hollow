from __future__ import annotations

from sqlalchemy.orm import Session

from app import crud
from app.models.user import User


def get_display_identity(db: Session, user_id: int, post_id: int, is_anonymous: bool):
    """返回 (nickname, avatar)。匿名时返回楼内一致的随机昵称。"""
    u = crud.user.user.get(db, user_id)
    if not u:
        return ("已注销用户", "")
    if is_anonymous:
        profile = crud.user.anon_profile.get_or_create(db, user_id=u.id, post_id=post_id)
        return (profile.nickname, profile.avatar)
    return (u.real_name or u.student_id, u.avatar)
