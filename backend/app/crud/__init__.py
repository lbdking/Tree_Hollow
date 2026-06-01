"""CRUD 数据访问层统一入口。"""
from app.crud import ai, appointment, content, group, hollow, knowledge, notification, stats, user

__all__ = [
    "ai",
    "appointment",
    "content",
    "group",
    "hollow",
    "knowledge",
    "notification",
    "stats",
    "user",
]
