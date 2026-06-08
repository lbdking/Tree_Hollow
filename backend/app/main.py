from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    import app.models  # noqa: F401  确保模型已注册
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running"}


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(api_router, prefix="/api/v1")
