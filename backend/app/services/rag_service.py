"""RAG 服务：文件解析、切分、Embedding、向量入库、相似度检索。

向量存储设计（Redis）：
- 全局 set    rag:user:{uid}:chunks     存储所有 chunk_id（user 维度）
- 文件 set    rag:file:{fid}:chunks     存储该文件的 chunk_id 列表
- chunk hash  rag:chunk:{cid}           {file_id, user_id, text, vector(b64)}
"""
from __future__ import annotations

import base64
import hashlib
import io
import re
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import redis

from app.core.config import settings


# ---------- Redis 客户端 ----------
_redis: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
    return _redis


# ---------- 文件解析 ----------
def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            return "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception as e:
            raise RuntimeError(f"PDF 解析失败: {e}")
    if name.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            raise RuntimeError(f"DOCX 解析失败: {e}")
    if name.endswith((".txt", ".md", ".markdown")):
        for enc in ("utf-8", "gbk", "latin-1"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="ignore")
    raise RuntimeError(f"不支持的文件类型: {filename}（仅支持 .pdf .docx .txt .md）")


# ---------- 切分 ----------
def split_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
    overlap = overlap or settings.RAG_CHUNK_OVERLAP
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + chunk_size, n)
        chunks.append(text[i:end].strip())
        if end >= n:
            break
        i = end - overlap
        if i <= 0:
            i = end
    return [c for c in chunks if c]


# ---------- Embedding ----------
def _hash_embedding(text: str, dim: int = None) -> np.ndarray:
    """无 API key 时的兜底 embedding：基于 char-trigram + 多 hash 桶 + L2 归一化。
    虽然不如真模型，但能跑出有意义的语义近似（同主题文本相似度更高）。
    """
    dim = dim or settings.EMBEDDING_DIM
    vec = np.zeros(dim, dtype=np.float32)
    if not text:
        return vec
    text = text.lower()
    # char trigram
    grams = [text[i : i + 3] for i in range(max(1, len(text) - 2))] or [text]
    for g in grams:
        for salt in range(4):
            h = int(hashlib.md5(f"{salt}:{g}".encode()).hexdigest(), 16)
            idx = h % dim
            sign = 1 if (h >> 12) & 1 else -1
            vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def _api_embedding(texts: List[str]) -> Optional[List[np.ndarray]]:
    """如果配置了 EMBEDDING_API_BASE，就走 OpenAI 兼容 API。否则返回 None。"""
    if not (settings.EMBEDDING_API_BASE and settings.EMBEDDING_API_KEY and settings.EMBEDDING_MODEL):
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.EMBEDDING_API_KEY, base_url=settings.EMBEDDING_API_BASE)
        resp = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=texts)
        return [np.array(d.embedding, dtype=np.float32) for d in resp.data]
    except Exception:
        return None


def embed_texts(texts: List[str]) -> List[np.ndarray]:
    if not texts:
        return []
    api_vecs = _api_embedding(texts)
    if api_vecs:
        # 归一化
        return [v / (np.linalg.norm(v) + 1e-9) for v in api_vecs]
    return [_hash_embedding(t) for t in texts]


# ---------- Redis 向量存取 ----------
def _vec_to_b64(v: np.ndarray) -> bytes:
    return base64.b64encode(v.astype(np.float32).tobytes())


def _b64_to_vec(b: bytes) -> np.ndarray:
    return np.frombuffer(base64.b64decode(b), dtype=np.float32)


@dataclass
class ChunkRecord:
    chunk_id: str
    file_id: int
    user_id: int
    text: str
    score: float = 0.0


def store_chunks(*, user_id: int, file_id: int, chunks: List[str], vectors: List[np.ndarray]) -> int:
    r = get_redis()
    pipe = r.pipeline()
    user_key = f"rag:user:{user_id}:chunks"
    file_key = f"rag:file:{file_id}:chunks"
    cnt = 0
    for text, vec in zip(chunks, vectors):
        cid = uuid.uuid4().hex
        chunk_key = f"rag:chunk:{cid}"
        pipe.hset(
            chunk_key,
            mapping={
                "file_id": str(file_id),
                "user_id": str(user_id),
                "text": text.encode("utf-8"),
                "vector": _vec_to_b64(vec),
            },
        )
        pipe.sadd(user_key, cid)
        pipe.sadd(file_key, cid)
        cnt += 1
    pipe.execute()
    return cnt


def delete_file_chunks(*, user_id: int, file_id: int) -> int:
    r = get_redis()
    file_key = f"rag:file:{file_id}:chunks"
    user_key = f"rag:user:{user_id}:chunks"
    cids = r.smembers(file_key)
    if not cids:
        return 0
    pipe = r.pipeline()
    for cid_b in cids:
        cid = cid_b.decode() if isinstance(cid_b, bytes) else cid_b
        pipe.delete(f"rag:chunk:{cid}")
        pipe.srem(user_key, cid)
    pipe.delete(file_key)
    pipe.execute()
    return len(cids)


def search(
    user_id: int,
    query: str,
    top_k: int = None,
    score_threshold: float = None,
    file_ids: Optional[List[int]] = None,
) -> List[ChunkRecord]:
    """在该用户的知识库中按 cosine 相似度 Top-K 检索。"""
    if not query.strip():
        return []
    top_k = top_k or settings.RAG_TOP_K
    threshold = score_threshold if score_threshold is not None else settings.RAG_SCORE_THRESHOLD

    r = get_redis()
    if file_ids:
        cids = set()
        for fid in file_ids:
            cids.update(r.smembers(f"rag:file:{fid}:chunks"))
    else:
        cids = r.smembers(f"rag:user:{user_id}:chunks")

    if not cids:
        return []

    q_vec = embed_texts([query])[0]

    # 批量取
    pipe = r.pipeline()
    cid_list = [c.decode() if isinstance(c, bytes) else c for c in cids]
    for cid in cid_list:
        pipe.hgetall(f"rag:chunk:{cid}")
    raws = pipe.execute()

    results: List[ChunkRecord] = []
    for cid, raw in zip(cid_list, raws):
        if not raw:
            continue
        # raw 的 key 可能是 bytes
        text = raw.get(b"text") or raw.get("text")
        vec_b = raw.get(b"vector") or raw.get("vector")
        file_id = int((raw.get(b"file_id") or raw.get("file_id") or b"0"))
        if not vec_b:
            continue
        v = _b64_to_vec(vec_b)
        score = float(np.dot(q_vec, v))
        if score < threshold:
            continue
        results.append(
            ChunkRecord(
                chunk_id=cid,
                file_id=file_id,
                user_id=user_id,
                text=text.decode("utf-8") if isinstance(text, bytes) else (text or ""),
                score=score,
            )
        )
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:top_k]


# ---------- Prompt 拼接 ----------
def build_rag_context(records: List[ChunkRecord], max_chars: int = 1500) -> str:
    if not records:
        return ""
    pieces = []
    used = 0
    for i, r in enumerate(records, 1):
        seg = f"【片段 {i} · 相似度 {r.score:.2f}】\n{r.text}"
        if used + len(seg) > max_chars:
            seg = seg[: max_chars - used]
            pieces.append(seg)
            break
        pieces.append(seg)
        used += len(seg)
    return "\n\n".join(pieces)


# ---------- 高层接口 ----------
def ingest_file(*, user_id: int, file_id: int, filename: str, data: bytes) -> Tuple[int, int]:
    """返回 (chunk_count, total_chars)"""
    text = extract_text(filename, data)
    chunks = split_text(text)
    if not chunks:
        return 0, 0
    vecs = embed_texts(chunks)
    store_chunks(user_id=user_id, file_id=file_id, chunks=chunks, vectors=vecs)
    return len(chunks), len(text)
