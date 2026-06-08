from __future__ import annotations

from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.knowledge import KnowledgeFile


class CRUDKnowledgeFile(CRUDBase[KnowledgeFile, dict, dict]):
    def list_by_user(self, db: Session, user_id: int) -> List[KnowledgeFile]:
        return (
            db.query(KnowledgeFile)
            .filter(KnowledgeFile.user_id == user_id)
            .order_by(desc(KnowledgeFile.created_at))
            .all()
        )

    def list_enabled(self, db: Session, user_id: int) -> List[KnowledgeFile]:
        return (
            db.query(KnowledgeFile)
            .filter(
                KnowledgeFile.user_id == user_id,
                KnowledgeFile.is_enabled == True,
                KnowledgeFile.status == "ready",
            )
            .all()
        )

    def get_user_file(self, db: Session, fid: int, user_id: int):
        return (
            db.query(KnowledgeFile)
            .filter(KnowledgeFile.id == fid, KnowledgeFile.user_id == user_id)
            .first()
        )


knowledge_file = CRUDKnowledgeFile(KnowledgeFile)
