"""
Configuration for AI Service
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "ai-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
    
    # MCP Configuration
    MCP_BASE_URL: str = "https://api.openai.com"
    MCP_API_KEY: str = ""  # Set in .env
    MCP_PROVIDER: str = "openai"  # openai, anthropic, local
    
    # AI Model Defaults
    DEFAULT_MODEL: str = "gpt-4-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
