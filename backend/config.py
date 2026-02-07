"""
Backend Configuration
====================

Centralized configuration using Pydantic settings.
Reads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "AI Multi-Agent Council API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./brand_config.db",
        description="Database connection URL"
    )
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ],
        description="Allowed CORS origins"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 100
    
    # AgenticEnv Integration
    AGENTIC_ENV_PATH: str = "../AgenticEnv"
    COUNCIL_DB_PATH: str = "../AgenticEnv/db/council.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
