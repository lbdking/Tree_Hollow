from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "TreeHollow"
    APP_ENV: str = "dev"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str = "mysql+pymysql://root:@127.0.0.1:3306/tree_hollow?charset=utf8mb4"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    AI_CONTEXT_WINDOW: int = 20
    AI_CACHE_FILE: str = "./data/ai_cache.json"

    # ---------- RAG ----------
    EMBEDDING_DIM: int = 256
    RAG_CHUNK_SIZE: int = 400
    RAG_CHUNK_OVERLAP: int = 80
    RAG_TOP_K: int = 4
    RAG_SCORE_THRESHOLD: float = 0.05
    EMBEDDING_API_BASE: str = ""
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_MODEL: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
