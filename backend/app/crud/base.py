"""通用 CRUD 基类：实现常用的增删改查方法，子类只需声明 model 即可。"""
from __future__ import annotations

from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ---------- 查询 ----------
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by(self, db: Session, **filters) -> Optional[ModelType]:
        q = db.query(self.model)
        for k, v in filters.items():
            q = q.filter(getattr(self.model, k) == v)
        return q.first()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        order_by: Any = None,
        **filters,
    ) -> List[ModelType]:
        q = db.query(self.model)
        for k, v in filters.items():
            if v is None:
                continue
            q = q.filter(getattr(self.model, k) == v)
        if order_by is not None:
            q = q.order_by(order_by)
        return q.offset(skip).limit(limit).all()

    def count(self, db: Session, **filters) -> int:
        q = db.query(self.model)
        for k, v in filters.items():
            if v is None:
                continue
            q = q.filter(getattr(self.model, k) == v)
        return q.count()

    # ---------- 写入 ----------
    def create(self, db: Session, *, obj_in: CreateSchemaType | dict, **extra) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=False)
        data.update(extra)
        obj = self.model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict,
    ) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for k, v in data.items():
            if hasattr(db_obj, k):
                setattr(db_obj, k, v)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
