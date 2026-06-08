from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import admin_required, get_current_user
from app.models.appointment import Appointment, Counselor
from app.models.user import User
from app.schemas import (
    AppointmentIn,
    AppointmentOut,
    AppointmentStatusIn,
    CounselorIn,
    CounselorOut,
)
from app.services import notify

router = APIRouter(prefix="/appointment", tags=["appointment"])


def _counselor_out(c: Counselor) -> CounselorOut:
    try:
        slots = json.loads(c.available_slots or "[]")
    except Exception:
        slots = []
    return CounselorOut(
        id=c.id,
        name=c.name,
        title=c.title,
        avatar=c.avatar,
        expertise=c.expertise,
        introduction=c.introduction,
        available_slots=slots,
        rating=c.rating,
    )


def _appointment_out(db: Session, a: Appointment) -> AppointmentOut:
    out = AppointmentOut.model_validate(a)
    c = crud.appointment.counselor.get(db, a.counselor_id)
    if c:
        out.counselor_name = c.name
    u = crud.user.user.get(db, a.user_id)
    if u:
        out.student_name = u.real_name or u.student_id
    return out


# ---------- 咨询师 ----------
@router.get("/counselors")
def list_counselors(db: Session = Depends(get_db)):
    items = crud.appointment.counselor.list_active(db)
    return {"items": [_counselor_out(c) for c in items]}


@router.get("/counselors/{cid}", response_model=CounselorOut)
def get_counselor(cid: int, db: Session = Depends(get_db)):
    c = crud.appointment.counselor.get(db, cid)
    if not c:
        raise HTTPException(404, "咨询师不存在")
    return _counselor_out(c)


@router.post("/counselors", response_model=CounselorOut)
def create_counselor(payload: CounselorIn, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    u = crud.user.user.get(db, payload.user_id)
    if not u:
        raise HTTPException(404, "对应用户不存在")
    crud.user.user.set_role(db, u, "counselor")
    c = crud.appointment.counselor.create(
        db,
        obj_in={
            "user_id": payload.user_id,
            "name": payload.name,
            "title": payload.title,
            "avatar": payload.avatar,
            "expertise": payload.expertise,
            "introduction": payload.introduction,
            "available_slots": json.dumps(payload.available_slots, ensure_ascii=False),
        },
    )
    return _counselor_out(c)


@router.put("/counselors/{cid}", response_model=CounselorOut)
def update_counselor(cid: int, payload: CounselorIn, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    c = crud.appointment.counselor.get(db, cid)
    if not c:
        raise HTTPException(404, "不存在")
    c = crud.appointment.counselor.update(
        db,
        db_obj=c,
        obj_in={
            "name": payload.name,
            "title": payload.title,
            "avatar": payload.avatar,
            "expertise": payload.expertise,
            "introduction": payload.introduction,
            "available_slots": json.dumps(payload.available_slots, ensure_ascii=False),
        },
    )
    return _counselor_out(c)


@router.delete("/counselors/{cid}")
def delete_counselor(cid: int, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    c = crud.appointment.counselor.get(db, cid)
    if not c:
        raise HTTPException(404, "不存在")
    crud.appointment.counselor.deactivate(db, c)
    return {"ok": True}


# ---------- 预约 ----------
@router.post("/appointments", response_model=AppointmentOut)
def create_appointment(payload: AppointmentIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = crud.appointment.counselor.get(db, payload.counselor_id)
    if not c or not c.is_active:
        raise HTTPException(404, "咨询师不存在")
    a = crud.appointment.appointment.create(
        db,
        obj_in={
            "user_id": user.id,
            "counselor_id": payload.counselor_id,
            "appointment_time": payload.appointment_time,
            "duration_minutes": payload.duration_minutes,
            "topic": payload.topic,
            "description": payload.description,
            "contact": payload.contact,
            "status": "pending",
        },
    )
    notify.push(db, c.user_id, "appointment", "新的预约申请", f"{user.real_name or '匿名同学'} 申请了一次咨询", link=f"/appointment/{a.id}")
    return _appointment_out(db, a)


@router.get("/appointments/my")
def my_appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = crud.appointment.appointment.list_by_user(db, user.id)
    return {"items": [_appointment_out(db, a) for a in items]}


@router.get("/appointments/counselor")
def counselor_appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in ("counselor", "admin"):
        raise HTTPException(403, "仅咨询师可访问")
    if user.role == "admin":
        items = crud.appointment.appointment.list_all(db)
    else:
        c = crud.appointment.counselor.get_by_user(db, user.id)
        if not c:
            raise HTTPException(404, "未找到咨询师档案")
        items = crud.appointment.appointment.list_by_counselor(db, c.id)
    return {"items": [_appointment_out(db, a) for a in items]}


@router.put("/appointments/{aid}/status", response_model=AppointmentOut)
def update_status(aid: int, payload: AppointmentStatusIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = crud.appointment.appointment.get(db, aid)
    if not a:
        raise HTTPException(404, "预约不存在")
    c = crud.appointment.counselor.get(db, a.counselor_id)
    if user.role == "admin":
        pass
    elif user.role == "counselor" and c and c.user_id == user.id:
        pass
    elif user.id == a.user_id and payload.status == "cancelled":
        pass
    else:
        raise HTTPException(403, "无权操作")
    a = crud.appointment.appointment.update_status(
        db, a, status=payload.status, counselor_note=payload.counselor_note or None
    )
    notify.push(db, a.user_id, "appointment", "预约状态更新", f"你的预约状态变更为：{payload.status}", link=f"/appointment/{a.id}")
    return _appointment_out(db, a)
