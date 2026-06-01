from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.group import GroupActivity, SupportGroup
from app.models.user import User
from app.schemas import ActivityIn, ActivityOut, GroupIn, GroupOut
from app.services import notify

router = APIRouter(prefix="/group", tags=["group"])


def _group_out(db: Session, g: SupportGroup, user: User) -> GroupOut:
    joined = crud.group.group_member.find(db, g.id, user.id) is not None
    out = GroupOut.model_validate(g)
    out.is_joined = joined
    return out


def _activity_out(db: Session, a: GroupActivity, user: User) -> ActivityOut:
    e = crud.group.enrollment.find(db, a.id, user.id)
    g = crud.group.support_group.get(db, a.group_id)
    out = ActivityOut.model_validate(a)
    out.is_enrolled = bool(e and e.status == "enrolled")
    out.group_name = g.name if g else ""
    return out


@router.get("/groups")
def list_groups(topic: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = crud.group.support_group.list_active(db, topic)
    return {"items": [_group_out(db, g, user) for g in items]}


@router.post("/groups", response_model=GroupOut)
def create_group(payload: GroupIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    g = crud.group.support_group.create(
        db,
        obj_in=payload,
        created_by=user.id,
        member_count=1,
    )
    crud.group.group_member.create(db, obj_in={"group_id": g.id, "user_id": user.id, "role": "owner"})
    return _group_out(db, g, user)


@router.get("/groups/{gid}", response_model=GroupOut)
def get_group(gid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    g = crud.group.support_group.get(db, gid)
    if not g:
        raise HTTPException(404, "小组不存在")
    return _group_out(db, g, user)


@router.post("/groups/{gid}/join")
def join_group(gid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    g = crud.group.support_group.get(db, gid)
    if not g:
        raise HTTPException(404, "小组不存在")
    if crud.group.group_member.find(db, gid, user.id):
        return {"ok": True}
    crud.group.group_member.create(db, obj_in={"group_id": gid, "user_id": user.id, "role": "member"})
    crud.group.support_group.adjust_member_count(db, g, 1)
    return {"ok": True}


@router.post("/groups/{gid}/leave")
def leave_group(gid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    m = crud.group.group_member.find(db, gid, user.id)
    if not m:
        return {"ok": True}
    crud.group.group_member.remove(db, id=m.id)
    g = crud.group.support_group.get(db, gid)
    if g:
        crud.group.support_group.adjust_member_count(db, g, -1)
    return {"ok": True}


# ---------- 活动 ----------
@router.get("/activities")
def list_activities(
    group_id: int | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = crud.group.activity.list_filter(db, group_id=group_id, status=status_filter)
    return {"items": [_activity_out(db, a, user) for a in items]}


@router.post("/activities", response_model=ActivityOut)
def create_activity(payload: ActivityIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    g = crud.group.support_group.get(db, payload.group_id)
    if not g:
        raise HTTPException(404, "小组不存在")
    if user.role != "admin":
        m = crud.group.group_member.find(db, payload.group_id, user.id)
        if not m or m.role not in ("owner", "admin"):
            raise HTTPException(403, "需要小组管理员权限")
    a = crud.group.activity.create(db, obj_in=payload)
    return _activity_out(db, a, user)


@router.post("/activities/{aid}/enroll")
def enroll_activity(aid: int, note: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = crud.group.activity.get(db, aid)
    if not a:
        raise HTTPException(404, "活动不存在")
    if a.status != "open":
        raise HTTPException(400, "活动未开放报名")
    e = crud.group.enrollment.find(db, aid, user.id)
    if e and e.status == "enrolled":
        return {"ok": True}
    if a.enrolled_count >= a.capacity:
        raise HTTPException(400, "活动已满")
    if e:
        crud.group.enrollment.update(db, db_obj=e, obj_in={"status": "enrolled", "note": note})
    else:
        crud.group.enrollment.create(
            db, obj_in={"activity_id": aid, "user_id": user.id, "note": note, "status": "enrolled"}
        )
    crud.group.activity.adjust_enrolled(db, a, 1)
    notify.push(db, user.id, "activity", "报名成功", f"已成功报名《{a.title}》", link=f"/group/activity/{aid}")
    return {"ok": True}


@router.post("/activities/{aid}/cancel")
def cancel_enroll(aid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = crud.group.enrollment.find(db, aid, user.id)
    if not e or e.status != "enrolled":
        return {"ok": True}
    crud.group.enrollment.update(db, db_obj=e, obj_in={"status": "cancelled"})
    a = crud.group.activity.get(db, aid)
    if a:
        crud.group.activity.adjust_enrolled(db, a, -1)
    return {"ok": True}
