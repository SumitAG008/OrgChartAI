"""
Configuration settings for HRIS Service
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "your-encryption-key-for-credentials"
    
    # SuccessFactors OData API
    SUCCESSFACTORS_BASE_URL: str = "https://api.successfactors.eu"
    SUCCESSFACTORS_OAUTH_URL: str = "https://api.successfactors.eu/oauth/token"
    
    # Sync Settings
    SYNC_BATCH_SIZE: int = 100
    SYNC_MAX_RETRIES: int = 3
    SYNC_RETRY_DELAY: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
