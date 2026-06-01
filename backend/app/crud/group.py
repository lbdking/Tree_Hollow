from __future__ import annotations

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.group import (
    ActivityEnrollment,
    GroupActivity,
    GroupMember,
    SupportGroup,
)


class CRUDGroup(CRUDBase[SupportGroup, dict, dict]):
    def list_active(self, db: Session, topic: Optional[str] = None) -> List[SupportGroup]:
        q = db.query(SupportGroup).filter(SupportGroup.is_active == True)
        if topic:
            q = q.filter(SupportGroup.topic == topic)
        return q.order_by(desc(SupportGroup.member_count)).all()

    def adjust_member_count(self, db: Session, group: SupportGroup, delta: int):
        group.member_count = max(0, group.member_count + delta)
        db.commit()


class CRUDGroupMember(CRUDBase[GroupMember, dict, dict]):
    def find(self, db: Session, group_id: int, user_id: int) -> Optional[GroupMember]:
        return (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .first()
        )


class CRUDActivity(CRUDBase[GroupActivity, dict, dict]):
    def list_filter(
        self,
        db: Session,
        *,
        group_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[GroupActivity]:
        q = db.query(GroupActivity)
        if group_id:
            q = q.filter(GroupActivity.group_id == group_id)
        if status:
            q = q.filter(GroupActivity.status == status)
        return q.order_by(desc(GroupActivity.start_time)).all()

    def adjust_enrolled(self, db: Session, activity: GroupActivity, delta: int):
        activity.enrolled_count = max(0, activity.enrolled_count + delta)
        db.commit()


class CRUDEnrollment(CRUDBase[ActivityEnrollment, dict, dict]):
    def find(self, db: Session, activity_id: int, user_id: int) -> Optional[ActivityEnrollment]:
        return (
            db.query(ActivityEnrollment)
            .filter(
                ActivityEnrollment.activity_id == activity_id,
                ActivityEnrollment.user_id == user_id,
            )
            .first()
        )


support_group = CRUDGroup(SupportGroup)
group_member = CRUDGroupMember(GroupMember)
activity = CRUDActivity(GroupActivity)
enrollment = CRUDEnrollment(ActivityEnrollment)
