from sqlalchemy.orm import Session

from app import crud


def push(db: Session, user_id: int, ntype: str, title: str, content: str = "", link: str = ""):
    return crud.notification.notification.push(
        db, user_id=user_id, type=ntype, title=title, content=content, link=link
    )
