from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import AnonymousProfile, User
from app.utils.anonymizer import gen_anonymous_nickname


class CRUDUser(CRUDBase[User, dict, dict]):
    def get_by_student_id(self, db: Session, student_id: str) -> Optional[User]:
        return db.query(User).filter(User.student_id == student_id, User.is_deleted == False).first()

    def set_role(self, db: Session, user: User, role: str) -> User:
        user.role = role
        db.commit()
        db.refresh(user)
        return user


class CRUDAnonProfile(CRUDBase[AnonymousProfile, dict, dict]):
    def get_or_create(self, db: Session, user_id: int, post_id: int = 0) -> AnonymousProfile:
        profile = (
            db.query(AnonymousProfile)
            .filter(AnonymousProfile.user_id == user_id, AnonymousProfile.post_id == post_id)
            .first()
        )
        if profile:
            return profile
        nickname = gen_anonymous_nickname(f"{user_id}-{post_id}")
        profile = AnonymousProfile(user_id=user_id, post_id=post_id, nickname=nickname, avatar="")
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile


user = CRUDUser(User)
anon_profile = CRUDAnonProfile(AnonymousProfile)
