"""
Configuration management - Robust version
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os
import json
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings with robust parsing"""
    
    # API Keys
    DEEPSEEK_API_KEY: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGO_USER: Optional[str] = None
    MONGO_PASSWORD: Optional[str] = None
    MONGO_DB_NAME: str = "compliance_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: str = ".pdf,.docx,.txt"
    UPLOAD_DIR: str = "uploads"
    
    # CORS - Supports both JSON array and comma-separated string
    ALLOWED_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:5000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "deepseek-chat"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.3
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Parse ALLOWED_ORIGINS from environment variable.
        Handles both JSON arrays and comma-separated strings.
        """
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            
            # Try JSON parsing first (handles ["a","b"] format)
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
            except json.JSONDecodeError:
                pass
            
            # Fallback: comma-separated string (handles a,b,c format)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        return []
    
    @field_validator("MONGODB_URL", mode="before")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Ensure MongoDB URL is properly formatted"""
        if v and not v.startswith("mongodb"):
            logger.warning(f"Invalid MongoDB URL format: {v}")
        return v

settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("vectors", exist_ok=True)

# Log configuration (without sensitive data)
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"MongoDB: {settings.MONGODB_URL.split('@')[-1] if '@' in settings.MONGODB_URL else 'local'}")
logger.info(f"Redis: {settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else 'local'}")
logger.info(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")
