from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database — set via .env, no password default
    DATABASE_URL: str = "mysql+aiomysql://easygeo:@localhost:3306/easygeo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # App Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = ""  # Must be set via .env in production

    # Authentication — API key required for all endpoints
    API_KEY: str = ""  # Must be set via .env in production

    # CORS — restrict to actual frontend origins in production
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
