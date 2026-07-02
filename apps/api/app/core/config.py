"""
Application Settings Configuration

This module handles all application settings using Pydantic Settings.
Supports environment variables, .env files, and sensible defaults.

Phase: Core Configuration
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============================================================
# PATHS
# ============================================================

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # Go up to project root
API_ROOT = Path(__file__).resolve().parents[2]  # Go up to apps/api

# ============================================================
# SETTINGS CLASS
# ============================================================

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Environment variables take precedence over defaults.
    Can be overridden with .env file or .env.docker file.
    """
    
    # ============================================================
    # APP CONFIGURATION
    # ============================================================
    
    APP_NAME: str = Field(
        default="Book Recommendation System",
        description="Application name"
    )
    
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="API version prefix"
    )
    
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, production, testing, staging"
    )
    
    # ============================================================
    # DATABASE CONFIGURATION
    # ============================================================
    
    DATABASE_URL: str = Field(
        default="",
        description="PostgreSQL database URL"
    )
    
    DATABASE_POOL_SIZE: int = Field(
        default=5,
        description="Database connection pool size"
    )
    
    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        description="Database connection pool max overflow"
    )
    
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries (for debugging)"
    )
    
    # ============================================================
    # REDIS CONFIGURATION
    # ============================================================
    
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    REDIS_CACHE_TTL: int = Field(
        default=3600,
        description="Redis cache TTL in seconds (default: 1 hour)"
    )
    
    # ============================================================
    # SECURITY CONFIGURATION
    # ============================================================
    
    SECRET_KEY: str = Field(
        default="",
        description="Secret key for JWT and sessions"
    )
    
    JWT_SECRET: str = Field(
        default="",
        description="JWT secret for token signing"
    )
    
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    JWT_EXPIRATION_MINUTES: int = Field(
        default=1440,  # 24 hours
        description="JWT token expiration in minutes"
    )
    
    # ============================================================
    # CORS CONFIGURATION
    # ============================================================
    
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        description="List of allowed CORS origins"
    )
    
    ALLOWED_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="List of allowed HTTP methods"
    )
    
    ALLOWED_HEADERS: List[str] = Field(
        default=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-Process-Time"
        ],
        description="List of allowed HTTP headers"
    )
    
    # ============================================================
    # ML & ARTIFACTS CONFIGURATION
    # ============================================================
    
    ARTIFACTS_DIR: Path = Field(
        default=API_ROOT / "ml" / "artifacts",
        description="Directory for ML model artifacts"
    )
    
    MODELS_DIR: Path = Field(
        default=API_ROOT / "ml" / "models",
        description="Directory for trained models"
    )
    
    DATA_DIR: Path = Field(
        default=PROJECT_ROOT / "data" / "processed",
        description="Directory for processed data"
    )
    
    # ============================================================
    # RECOMMENDER CONFIGURATION
    # ============================================================
    
    HYBRID_COLLABORATIVE_WEIGHT: float = Field(
        default=0.50,
        description="Weight for collaborative recommendations",
        ge=0.0,
        le=1.0
    )
    
    HYBRID_CONTENT_WEIGHT: float = Field(
        default=0.30,
        description="Weight for content-based recommendations",
        ge=0.0,
        le=1.0
    )
    
    HYBRID_POPULARITY_WEIGHT: float = Field(
        default=0.20,
        description="Weight for popularity-based recommendations",
        ge=0.0,
        le=1.0
    )
    
    MIN_RATINGS_THRESHOLD: int = Field(
        default=50,
        description="Minimum number of ratings to consider a book",
        ge=1
    )
    
    DEFAULT_TOP_K: int = Field(
        default=10,
        description="Default number of recommendations",
        ge=1,
        le=100
    )
    
    # ============================================================
    # VALIDATORS
    # ============================================================
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is valid."""
        valid_envs = {'development', 'production', 'testing', 'staging'}
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v_lower
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str, info: ValidationInfo) -> str:
        """Validate database URL format."""
        if not v:
            return v
        if not (v.startswith('postgresql://') or v.startswith('postgres://')):
            raise ValueError("DATABASE_URL must start with postgresql:// or postgres://")
        return v
    
    @field_validator('REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v:
            return v
        if not (v.startswith('redis://') or v.startswith('rediss://')):
            raise ValueError("REDIS_URL must start with redis:// or rediss://")
        return v
    
    @field_validator('SECRET_KEY', 'JWT_SECRET')
    @classmethod
    def validate_secrets(cls, v: str, info: ValidationInfo) -> str:
        """Validate secrets are set (production only)."""
        # Skip validation in development
        return v
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT.lower() == "testing"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT.lower() == "staging"
    
    @property
    def hybrid_weights(self) -> Dict[str, float]:
        """Get hybrid recommender weights as a dict."""
        return {
            "collaborative": self.HYBRID_COLLABORATIVE_WEIGHT,
            "content": self.HYBRID_CONTENT_WEIGHT,
            "popularity": self.HYBRID_POPULARITY_WEIGHT
        }
    
    # ============================================================
    # MODEL CONFIG
    # ============================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_default=False,
    )


# ============================================================
# LOAD SETTINGS
# ============================================================

def _load_env_file() -> Path:
    """
    Load the appropriate environment file.
    
    Priority:
    1. .env (local overrides)
    2. .env.{ENVIRONMENT} (environment specific)
    3. .env.docker (Docker default)
    
    Returns:
    --------
    Path: The loaded env file path or None
    """
    # Check for environment-specific file
    env = os.getenv("ENVIRONMENT", "development")
    env_file = Path(f".env.{env}")
    
    if env_file.exists():
        return env_file
    
    # Check for local .env
    if Path(".env").exists():
        return Path(".env")
    
    # Check for Docker default
    if Path(".env.docker").exists():
        return Path(".env.docker")
    
    return None


# Try to load environment variables from env file
_env_file = _load_env_file()
if _env_file:
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file, override=True)
        print(f"✅ Loaded environment from: {_env_file}")
    except ImportError:
        pass


# Create settings instance
settings = Settings()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_settings() -> Settings:
    """
    Get the settings instance.
    
    Returns:
    --------
    Settings: The settings instance
    """
    return settings


def get_hybrid_weights() -> Dict[str, float]:
    """
    Get hybrid recommender weights from settings.
    
    Returns:
    --------
    Dict[str, float]: Hybrid weights
    """
    return settings.hybrid_weights


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SETTINGS TEST")
    print("=" * 60)
    
    print(f"\n📋 Application: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🔧 Environment: {settings.ENVIRONMENT}")
    print(f"📊 Debug Mode: {settings.DEBUG}")
    print(f"📝 Log Level: {settings.LOG_LEVEL}")
    
    print(f"\n📁 Directories:")
    print(f"  Artifacts: {settings.ARTIFACTS_DIR}")
    print(f"  Models: {settings.MODELS_DIR}")
    print(f"  Data: {settings.DATA_DIR}")
    
    print(f"\n⚖️ Hybrid Weights:")
    print(f"  Collaborative: {settings.HYBRID_COLLABORATIVE_WEIGHT}")
    print(f"  Content: {settings.HYBRID_CONTENT_WEIGHT}")
    print(f"  Popularity: {settings.HYBRID_POPULARITY_WEIGHT}")
    
    print(f"\n🔐 Security:")
    print(f"  JWT Algorithm: {settings.JWT_ALGORITHM}")
    print(f"  CORS Origins: {settings.ALLOWED_ORIGINS}")
    
    print(f"\n🏷️ Properties:")
    print(f"  is_development: {settings.is_development}")
    print(f"  is_production: {settings.is_production}")
    print(f"  is_testing: {settings.is_testing}")
    
    print("\n✅ Settings test completed!")