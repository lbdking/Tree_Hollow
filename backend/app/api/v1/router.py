from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    ai,
    appointment,
    auth,
    content,
    group,
    hollow,
    knowledge,
    notification,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(hollow.router)
api_router.include_router(content.router)
api_router.include_router(group.router)
api_router.include_router(appointment.router)
api_router.include_router(notification.router)
api_router.include_router(ai.router)
api_router.include_router(knowledge.router)
api_router.include_router(admin.router)
