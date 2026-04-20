from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database — set via .env, no password default
    DATABASE_URL: str = "mysql+aiomysql://easygeo:@localhost:3306/easygeo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # App Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str  # Required — must be set via .env

    # Authentication — API key required for all endpoints
    API_KEY: str  # Required — must be set via .env

    # CORS — restrict to actual frontend origins in production
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # DB Connection Pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("SECRET_KEY", "API_KEY")
    @classmethod
    def must_not_be_empty(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(
                f"{info.field_name}은(는) .env 파일에 반드시 설정되어야 합니다"
            )
        return v


settings = Settings()
