from __future__ import annotations

from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.ai import AiChatMessage, AiChatSession


class CRUDAiSession(CRUDBase[AiChatSession, dict, dict]):
    def list_by_user(self, db: Session, user_id: int) -> List[AiChatSession]:
        return (
            db.query(AiChatSession)
            .filter(AiChatSession.user_id == user_id)
            .order_by(desc(AiChatSession.updated_at))
            .all()
        )

    def get_user_session(self, db: Session, sid: int, user_id: int):
        return (
            db.query(AiChatSession)
            .filter(AiChatSession.id == sid, AiChatSession.user_id == user_id)
            .first()
        )

    def touch(self, db: Session, session: AiChatSession):
        from datetime import datetime
        session.updated_at = datetime.utcnow()
        db.commit()


class CRUDAiMessage(CRUDBase[AiChatMessage, dict, dict]):
    def list_by_session(self, db: Session, session_id: int) -> List[AiChatMessage]:
        return (
            db.query(AiChatMessage)
            .filter(AiChatMessage.session_id == session_id)
            .order_by(AiChatMessage.id.asc())
            .all()
        )

    def delete_by_session(self, db: Session, session_id: int):
        db.query(AiChatMessage).filter(AiChatMessage.session_id == session_id).delete()
        db.commit()

    def append(self, db: Session, *, session_id: int, role: str, content: str) -> AiChatMessage:
        m = AiChatMessage(session_id=session_id, role=role, content=content)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m


ai_session = CRUDAiSession(AiChatSession)
ai_message = CRUDAiMessage(AiChatMessage)
