from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas import NotificationOut

router = APIRouter(prefix="/notification", tags=["notification"])


@router.get("/list")
def list_notifications(page: int = 1, size: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total, items = crud.notification.notification.list_for_user(db, user.id, page, size)
    return {"total": total, "items": [NotificationOut.model_validate(n) for n in items]}


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"count": crud.notification.notification.unread_count(db, user.id)}


@router.post("/read/{nid}")
def mark_read(nid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = crud.notification.notification.get(db, nid)
    if n and n.user_id == user.id:
        crud.notification.notification.mark_read(db, n)
    return {"ok": True}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    crud.notification.notification.mark_all_read(db, user.id)
    return {"ok": True}
