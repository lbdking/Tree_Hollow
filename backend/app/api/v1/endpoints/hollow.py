from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.hollow import HollowPost, HollowReply
from app.models.user import User
from app.schemas import (
    HollowPostIn,
    HollowPostOut,
    HollowReplyIn,
    HollowReplyOut,
    ReportIn,
)
from app.services import notify
from app.services.identity import get_display_identity
from app.utils.crisis import CRISIS_HOTLINE_TEXT, detect_crisis

router = APIRouter(prefix="/hollow", tags=["hollow"])


def _post_to_out(db: Session, p: HollowPost, current_user: User) -> HollowPostOut:
    nickname, avatar = get_display_identity(db, p.user_id, p.id, p.is_anonymous)
    is_liked = crud.hollow.hollow_like.find(db, current_user.id, "post", p.id) is not None
    return HollowPostOut(
        id=p.id,
        content=p.content,
        mood_tag=p.mood_tag,
        nickname=nickname,
        avatar=avatar,
        is_mine=p.user_id == current_user.id,
        like_count=p.like_count,
        reply_count=p.reply_count,
        is_liked=is_liked,
        is_crisis=p.is_crisis,
        created_at=p.created_at,
    )


@router.get("/posts")
def list_posts(
    page: int = 1,
    size: int = 10,
    mood_tag: str | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total, items = crud.hollow.hollow_post.list_published(
        db, page=page, size=size, mood_tag=mood_tag, keyword=keyword
    )
    return {"total": total, "items": [_post_to_out(db, p, user) for p in items]}


@router.post("/posts", response_model=HollowPostOut)
def create_post(payload: HollowPostIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    is_crisis = detect_crisis(payload.content)
    p = crud.hollow.hollow_post.create(
        db,
        obj_in={
            "user_id": user.id,
            "content": payload.content,
            "mood_tag": payload.mood_tag,
            "is_anonymous": payload.is_anonymous,
            "is_crisis": is_crisis,
        },
    )
    if is_crisis:
        notify.push(
            db,
            user.id,
            "system",
            "我们看到了你的求助 💗",
            CRISIS_HOTLINE_TEXT,
            link=f"/hollow/{p.id}",
        )
    return _post_to_out(db, p, user)


@router.get("/posts/{post_id}", response_model=HollowPostOut)
def get_post(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = crud.hollow.hollow_post.get(db, post_id)
    if not p or p.status != "published":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "帖子不存在")
    return _post_to_out(db, p, user)


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = crud.hollow.hollow_post.get(db, post_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "帖子不存在")
    if p.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权操作")
    crud.hollow.hollow_post.set_status(db, p, "deleted")
    return {"ok": True}


@router.get("/posts/{post_id}/replies")
def list_replies(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rs = crud.hollow.hollow_reply.list_by_post(db, post_id)
    out = []
    for r in rs:
        nickname, avatar = get_display_identity(db, r.user_id, post_id, r.is_anonymous)
        out.append(
            HollowReplyOut(
                id=r.id,
                post_id=r.post_id,
                parent_id=r.parent_id,
                content=r.content,
                nickname=nickname,
                avatar=avatar,
                is_mine=r.user_id == user.id,
                like_count=r.like_count,
                created_at=r.created_at,
            )
        )
    return {"items": out}


@router.post("/posts/{post_id}/replies", response_model=HollowReplyOut)
def create_reply(
    post_id: int,
    payload: HollowReplyIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = crud.hollow.hollow_post.get(db, post_id)
    if not post or post.status != "published":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "帖子不存在")
    r = crud.hollow.hollow_reply.create(
        db,
        obj_in={
            "post_id": post_id,
            "user_id": user.id,
            "parent_id": payload.parent_id,
            "content": payload.content,
            "is_anonymous": payload.is_anonymous,
        },
    )
    crud.hollow.hollow_post.incr_reply_count(db, post, 1)

    if post.user_id != user.id:
        nickname, _ = get_display_identity(db, user.id, post_id, payload.is_anonymous)
        notify.push(
            db,
            post.user_id,
            "reply",
            f"{nickname} 回复了你的树洞",
            payload.content[:100],
            link=f"/hollow/{post_id}",
        )

    nickname, avatar = get_display_identity(db, r.user_id, post_id, r.is_anonymous)
    return HollowReplyOut(
        id=r.id,
        post_id=r.post_id,
        parent_id=r.parent_id,
        content=r.content,
        nickname=nickname,
        avatar=avatar,
        is_mine=True,
        like_count=0,
        created_at=r.created_at,
    )


@router.post("/like")
def toggle_like(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if target_type not in ("post", "reply"):
        raise HTTPException(400, "target_type 非法")
    existing = crud.hollow.hollow_like.find(db, user.id, target_type, target_id)
    if existing:
        crud.hollow.hollow_like.remove(db, id=existing.id)
        delta = -1
    else:
        crud.hollow.hollow_like.create(
            db,
            obj_in={"user_id": user.id, "target_type": target_type, "target_id": target_id},
        )
        delta = 1
    if target_type == "post":
        p = crud.hollow.hollow_post.get(db, target_id)
        if p:
            crud.hollow.hollow_post.adjust_like(db, p, delta)
    else:
        r = crud.hollow.hollow_reply.get(db, target_id)
        if r:
            crud.hollow.hollow_reply.adjust_like(db, r, delta)
    return {"liked": delta == 1, "delta": delta}


@router.post("/report")
def report_target(payload: ReportIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    crud.hollow.report.create(
        db,
        obj_in={
            "reporter_id": user.id,
            "target_type": payload.target_type,
            "target_id": payload.target_id,
            "reason": payload.reason,
        },
    )
    return {"ok": True}


@router.get("/my-posts")
def my_posts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = crud.hollow.hollow_post.list_my(db, user.id)
    return {"items": [_post_to_out(db, p, user) for p in items]}
