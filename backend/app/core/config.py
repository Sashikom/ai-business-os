from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Business OS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://aibos:aibos123@db:5432/aibos"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "aibos-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SUPER_ADMIN_EMAIL: str = "a.v.medvedev1985@gmail.com"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
