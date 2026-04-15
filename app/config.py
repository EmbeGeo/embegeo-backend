from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+aiomysql://easygeo:password123@localhost:3306/easygeo"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # App Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = (
        "your-secret-key-here"  # Consider using a more secure method for production
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
