from __future__ import annotations

import json
import os
import threading
from collections import defaultdict
from typing import AsyncIterator, Dict, List

from openai import OpenAI

from app.core.config import settings

SYSTEM_PROMPT = (
    "你是一名温暖、专业、富有耐心的心理陪伴助手，名字叫'树洞 AI'。"
    "你的任务是倾听用户的情绪，给予理解、共情和温柔的回应。"
    "请遵循：1) 不做精神医学诊断；2) 不轻视、不评判；3) 用温柔自然的中文短句；"
    "4) 当用户提及自伤、轻生等危机话题时，温柔地表达关切，并提示拨打全国心理援助热线 400-161-9995，"
    "或建议预约校园心理咨询师；5) 必要时引导用户做几次深呼吸、写下心情、或寻求亲友支持。"
)


class AiCache:
    """进程内消息缓存 + 落盘"""

    def __init__(self, cache_file: str, window: int = 20):
        self.cache_file = cache_file
        self.window = window
        self._mem: Dict[int, List[dict]] = defaultdict(list)
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    self._mem[int(k)] = v
        except Exception:
            pass

    def _persist(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in self._mem.items()}, f, ensure_ascii=False)

    def get(self, session_id: int) -> List[dict]:
        with self._lock:
            return list(self._mem.get(session_id, []))

    def append(self, session_id: int, role: str, content: str):
        with self._lock:
            arr = self._mem[session_id]
            arr.append({"role": role, "content": content})
            if len(arr) > self.window:
                self._mem[session_id] = arr[-self.window:]
            self._persist()

    def seed(self, session_id: int, messages: List[dict]):
        with self._lock:
            self._mem[session_id] = messages[-self.window:]
            self._persist()

    def clear(self, session_id: int):
        with self._lock:
            self._mem.pop(session_id, None)
            self._persist()


_cache: AiCache | None = None


def get_cache() -> AiCache:
    global _cache
    if _cache is None:
        _cache = AiCache(settings.AI_CACHE_FILE, settings.AI_CONTEXT_WINDOW)
    return _cache


def _client() -> OpenAI:
    return OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)


def build_messages(session_id: int, user_content: str, rag_context: str = "") -> List[dict]:
    history = get_cache().get(session_id)
    sys_prompt = SYSTEM_PROMPT
    if rag_context:
        sys_prompt += (
            "\n\n---\n以下是用户上传的资料中检索到的相关片段（仅供你回答时参考，"
            "若与用户问题不相关请忽略，不要编造内容）：\n" + rag_context
        )
    msgs = [{"role": "system", "content": sys_prompt}]
    msgs.extend(history)
    msgs.append({"role": "user", "content": user_content})
    return msgs


def stream_chat(session_id: int, user_content: str, rag_context: str = ""):
    """同步生成器：用于 FastAPI StreamingResponse(SSE)。"""
    messages = build_messages(session_id, user_content, rag_context)
    full_reply: list[str] = []
    try:
        client = _client()
        resp = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=messages,
            stream=True,
            temperature=0.8,
        )
        for chunk in resp:
            try:
                delta = chunk.choices[0].delta
                piece = getattr(delta, "content", None) or ""
            except Exception:
                piece = ""
            if piece:
                full_reply.append(piece)
                yield f"data: {json.dumps({'type':'delta','content':piece}, ensure_ascii=False)}\n\n"
    except Exception as e:
        err = f"[AI服务暂时不可用: {e}]"
        full_reply.append(err)
        yield f"data: {json.dumps({'type':'error','content':err}, ensure_ascii=False)}\n\n"

    final_text = "".join(full_reply)
    get_cache().append(session_id, "user", user_content)
    get_cache().append(session_id, "assistant", final_text)
    yield f"data: {json.dumps({'type':'done','content':final_text}, ensure_ascii=False)}\n\n"
