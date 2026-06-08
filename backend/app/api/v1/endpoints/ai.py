from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas import AiChatIn, AiMessageOut, AiSessionOut
from app.services import ai_service, rag_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = crud.ai.ai_session.list_by_user(db, user.id)
    return {"items": [AiSessionOut.model_validate(s) for s in items]}


@router.post("/sessions", response_model=AiSessionOut)
def create_session(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = crud.ai.ai_session.create(db, obj_in={"user_id": user.id, "title": "新对话"})
    return AiSessionOut.model_validate(s)


@router.get("/sessions/{sid}/messages")
def get_messages(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = crud.ai.ai_session.get_user_session(db, sid, user.id)
    if not s:
        raise HTTPException(404, "会话不存在")
    msgs = crud.ai.ai_message.list_by_session(db, sid)
    return {"items": [AiMessageOut.model_validate(m) for m in msgs]}


@router.delete("/sessions/{sid}")
def delete_session(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = crud.ai.ai_session.get_user_session(db, sid, user.id)
    if not s:
        return {"ok": True}
    crud.ai.ai_message.delete_by_session(db, sid)
    crud.ai.ai_session.remove(db, id=sid)
    ai_service.get_cache().clear(sid)
    return {"ok": True}


@router.post("/chat/stream")
def chat_stream(payload: AiChatIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """SSE 流式回复，可选 RAG 增强。"""
    sid = payload.session_id
    if not sid:
        s = crud.ai.ai_session.create(
            db, obj_in={"user_id": user.id, "title": payload.content[:20] or "新对话"}
        )
        sid = s.id
    else:
        s = crud.ai.ai_session.get_user_session(db, sid, user.id)
        if not s:
            raise HTTPException(404, "会话不存在")

    # 加载历史进缓存（首次）
    if not ai_service.get_cache().get(sid):
        history = crud.ai.ai_message.list_by_session(db, sid)
        ai_service.get_cache().seed(sid, [{"role": m.role, "content": m.content} for m in history])

    # 写入用户消息
    crud.ai.ai_message.append(db, session_id=sid, role="user", content=payload.content)

    # ---------- RAG 检索 ----------
    rag_context = ""
    rag_hits_meta: list[dict] = []
    if payload.use_rag:
        enabled = crud.knowledge.knowledge_file.list_enabled(db, user.id)
        if enabled:
            allowed_ids = [f.id for f in enabled]
            if payload.file_ids:
                allowed_ids = [i for i in allowed_ids if i in payload.file_ids]
            if allowed_ids:
                hits = rag_service.search(
                    user_id=user.id, query=payload.content, file_ids=allowed_ids
                )
                rag_context = rag_service.build_rag_context(hits)
                fid_to_name = {f.id: f.filename for f in enabled}
                rag_hits_meta = [
                    {
                        "file_id": h.file_id,
                        "filename": fid_to_name.get(h.file_id, ""),
                        "score": round(h.score, 3),
                        "preview": h.text[:80],
                    }
                    for h in hits
                ]

    def gen():
        yield f"data: {json.dumps({'type':'session','session_id':sid}, ensure_ascii=False)}\n\n"
        if rag_hits_meta:
            yield f"data: {json.dumps({'type':'rag','hits':rag_hits_meta}, ensure_ascii=False)}\n\n"
        for chunk in ai_service.stream_chat(sid, payload.content, rag_context):
            try:
                obj = json.loads(chunk.replace("data: ", "").strip())
                if obj.get("type") == "done":
                    final_text = obj.get("content", "")
                    db2 = SessionLocal()
                    try:
                        crud.ai.ai_message.append(db2, session_id=sid, role="assistant", content=final_text)
                        sess = crud.ai.ai_session.get(db2, sid)
                        if sess:
                            crud.ai.ai_session.touch(db2, sess)
                    finally:
                        db2.close()
            except Exception:
                pass
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")
