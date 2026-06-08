from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas import KnowledgeFileOut, KnowledgeSearchHit
from app.services import rag_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

ALLOWED_EXT = (".pdf", ".docx", ".txt", ".md", ".markdown")
MAX_BYTES = 20 * 1024 * 1024  # 20MB


@router.get("/files")
def list_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = crud.knowledge.knowledge_file.list_by_user(db, user.id)
    return {"items": [KnowledgeFileOut.model_validate(i) for i in items]}


@router.post("/files", response_model=KnowledgeFileOut)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    name = (file.filename or "unknown").lower()
    if not name.endswith(ALLOWED_EXT):
        raise HTTPException(400, f"仅支持 {', '.join(ALLOWED_EXT)} 格式")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "文件过大（≤ 20MB）")

    f = crud.knowledge.knowledge_file.create(
        db,
        obj_in={
            "user_id": user.id,
            "filename": file.filename,
            "mime_type": file.content_type or "",
            "size_bytes": len(data),
            "chunk_count": 0,
            "is_enabled": True,
            "status": "processing",
        },
    )
    try:
        chunk_count, _chars = rag_service.ingest_file(
            user_id=user.id, file_id=f.id, filename=file.filename, data=data
        )
        f = crud.knowledge.knowledge_file.update(
            db,
            db_obj=f,
            obj_in={"chunk_count": chunk_count, "status": "ready", "error_msg": ""},
        )
    except Exception as e:
        f = crud.knowledge.knowledge_file.update(
            db, db_obj=f, obj_in={"status": "failed", "error_msg": str(e)[:500]}
        )
        raise HTTPException(500, f"解析失败: {e}")
    return KnowledgeFileOut.model_validate(f)


@router.delete("/files/{fid}")
def delete_file(fid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = crud.knowledge.knowledge_file.get_user_file(db, fid, user.id)
    if not f:
        raise HTTPException(404, "文件不存在")
    rag_service.delete_file_chunks(user_id=user.id, file_id=fid)
    crud.knowledge.knowledge_file.remove(db, id=fid)
    return {"ok": True}


@router.put("/files/{fid}/toggle")
def toggle_enabled(fid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = crud.knowledge.knowledge_file.get_user_file(db, fid, user.id)
    if not f:
        raise HTTPException(404, "文件不存在")
    f = crud.knowledge.knowledge_file.update(db, db_obj=f, obj_in={"is_enabled": not f.is_enabled})
    return {"is_enabled": f.is_enabled}


@router.post("/search")
def search_kb(query: str, top_k: int = 4, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """前端可用于检索预览，肉眼查看 RAG 命中结果"""
    enabled = crud.knowledge.knowledge_file.list_enabled(db, user.id)
    fid_to_name = {f.id: f.filename for f in enabled}
    if not enabled:
        return {"items": []}
    hits = rag_service.search(user_id=user.id, query=query, top_k=top_k, file_ids=list(fid_to_name.keys()))
    return {
        "items": [
            KnowledgeSearchHit(
                file_id=h.file_id,
                filename=fid_to_name.get(h.file_id, ""),
                text=h.text,
                score=h.score,
            )
            for h in hits
        ]
    }
