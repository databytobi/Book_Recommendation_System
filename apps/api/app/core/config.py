from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Book Recommendation System"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    model_config = SettingsConfigDict(
        env_file=".env",  # Try .env first
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Try to load from .env.docker if .env doesn't exist
_env_file = Path(".env.docker")
if _env_file.exists() and not Path(".env").exists():
    import os
    # pyrefly: ignore [missing-import]
    from dotenv import load_dotenv
    load_dotenv(_env_file)

settings = Settings()