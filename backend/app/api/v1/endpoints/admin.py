from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import admin_required
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(admin_required)):
    return {
        "summary": crud.stats.stats.summary(db),
        "posts_week": crud.stats.stats.posts_in_recent_days(db, days=7),
        "mood_distribution": crud.stats.stats.mood_distribution(db),
    }


@router.get("/users")
def list_users(page: int = 1, size: int = 20, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    skip = (page - 1) * size
    items = crud.user.user.list(
        db, skip=skip, limit=size, order_by=desc(User.created_at), is_deleted=False
    )
    total = crud.user.user.count(db, is_deleted=False)
    return {
        "total": total,
        "items": [
            {"id": u.id, "student_id": u.student_id, "real_name": u.real_name, "role": u.role, "created_at": u.created_at}
            for u in items
        ],
    }


@router.put("/users/{uid}/role")
def set_role(uid: int, role: str, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    if role not in ("student", "counselor", "admin"):
        raise HTTPException(400, "非法角色")
    u = crud.user.user.get(db, uid)
    if not u:
        raise HTTPException(404, "用户不存在")
    crud.user.user.set_role(db, u, role)
    return {"ok": True}


# ---------- 审核 ----------
@router.get("/reports")
def list_reports(status_filter: str = "pending", db: Session = Depends(get_db), _: User = Depends(admin_required)):
    items = crud.hollow.report.list_by_status(db, status_filter)
    out = []
    for r in items:
        if r.target_type == "post":
            p = crud.hollow.hollow_post.get(db, r.target_id)
            target_content = p.content if p else "[已删除]"
        else:
            rp = crud.hollow.hollow_reply.get(db, r.target_id)
            target_content = rp.content if rp else "[已删除]"
        out.append(
            {
                "id": r.id,
                "reporter_id": r.reporter_id,
                "target_type": r.target_type,
                "target_id": r.target_id,
                "target_content": target_content,
                "reason": r.reason,
                "status": r.status,
                "created_at": r.created_at,
            }
        )
    return {"items": out}


@router.post("/reports/{rid}/handle")
def handle_report(rid: int, action: str, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    r = crud.hollow.report.get(db, rid)
    if not r:
        raise HTTPException(404, "举报不存在")
    if action in ("hide", "delete"):
        new_status = "hidden" if action == "hide" else "deleted"
        if r.target_type == "post":
            p = crud.hollow.hollow_post.get(db, r.target_id)
            if p:
                crud.hollow.hollow_post.set_status(db, p, new_status)
        else:
            rp = crud.hollow.hollow_reply.get(db, r.target_id)
            if rp:
                crud.hollow.hollow_reply.set_status(db, rp, new_status)
        crud.hollow.report.mark_handled(db, r, status="handled", admin_id=admin.id)
    elif action == "reject":
        crud.hollow.report.mark_handled(db, r, status="rejected", admin_id=admin.id)
    else:
        raise HTTPException(400, "未知动作")
    return {"ok": True}


@router.get("/posts")
def list_all_posts(page: int = 1, size: int = 20, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    total, items = crud.hollow.hollow_post.list_admin(db, page, size)
    return {
        "total": total,
        "items": [
            {
                "id": p.id, "user_id": p.user_id, "content": p.content, "mood_tag": p.mood_tag,
                "status": p.status, "is_crisis": p.is_crisis,
                "like_count": p.like_count, "reply_count": p.reply_count, "created_at": p.created_at,
            }
            for p in items
        ],
    }


@router.put("/posts/{pid}/status")
def admin_set_post_status(pid: int, status_v: str, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    p = crud.hollow.hollow_post.get(db, pid)
    if not p:
        raise HTTPException(404, "帖子不存在")
    if status_v not in ("published", "hidden", "deleted"):
        raise HTTPException(400, "非法状态")
    crud.hollow.hollow_post.set_status(db, p, status_v)
    return {"ok": True}
