from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import admin_required, get_current_user
from app.models.user import User
from app.schemas import ArticleIn, ArticleOut, BreathingIn, MoodIn, MoodOut

router = APIRouter(prefix="/content", tags=["content"])


# ---------- 科普 ----------
@router.get("/articles")
def list_articles(
    page: int = 1,
    size: int = 10,
    category: str | None = None,
    content_type: str | None = None,
    db: Session = Depends(get_db),
):
    total, items = crud.content.article.list_published(
        db, page=page, size=size, category=category, content_type=content_type
    )
    return {"total": total, "items": [ArticleOut.model_validate(a) for a in items]}


@router.get("/articles/{aid}", response_model=ArticleOut)
def get_article(aid: int, db: Session = Depends(get_db)):
    a = crud.content.article.get(db, aid)
    if not a or not a.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "内容不存在")
    crud.content.article.incr_view(db, a)
    return ArticleOut.model_validate(a)


@router.post("/articles", response_model=ArticleOut)
def create_article(payload: ArticleIn, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    a = crud.content.article.create(db, obj_in=payload)
    return ArticleOut.model_validate(a)


@router.put("/articles/{aid}", response_model=ArticleOut)
def update_article(aid: int, payload: ArticleIn, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    a = crud.content.article.get(db, aid)
    if not a:
        raise HTTPException(404, "不存在")
    a = crud.content.article.update(db, db_obj=a, obj_in=payload)
    return ArticleOut.model_validate(a)


@router.delete("/articles/{aid}")
def delete_article(aid: int, db: Session = Depends(get_db), _: User = Depends(admin_required)):
    a = crud.content.article.remove(db, id=aid)
    if not a:
        raise HTTPException(404, "不存在")
    return {"ok": True}


# ---------- 情绪打卡 ----------
@router.post("/mood", response_model=MoodOut)
def add_mood(payload: MoodIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rd = payload.record_date or date.today()
    m = crud.content.mood.upsert(
        db,
        user_id=user.id,
        record_date=rd,
        mood=payload.mood,
        score=payload.score,
        note=payload.note,
    )
    return MoodOut.model_validate(m)


@router.get("/mood")
def list_mood(
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = crud.content.mood.list_by_month(db, user_id=user.id, year=year, month=month)
    return {"items": [MoodOut.model_validate(m) for m in items]}


# ---------- 呼吸训练 ----------
@router.post("/breathing")
def add_breathing(payload: BreathingIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    b = crud.content.breathing.create(
        db,
        obj_in={
            "user_id": user.id,
            "duration_seconds": payload.duration_seconds,
            "cycles": payload.cycles,
        },
    )
    return {"ok": True, "id": b.id}


@router.get("/breathing/stats")
def breathing_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.content.breathing.stats(db, user.id)
