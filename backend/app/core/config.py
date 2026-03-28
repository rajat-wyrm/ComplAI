"""
Configuration management using Pydantic settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os
import json

class Settings(BaseSettings):
    """Application settings"""
    
    DEEPSEEK_API_KEY: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGO_USER: Optional[str] = None
    MONGO_PASSWORD: Optional[str] = None
    MONGO_DB_NAME: str = "compliance_db"
    
    REDIS_URL: str = "redis://localhost:6379"
    
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: str = ".pdf,.docx,.txt"
    UPLOAD_DIR: str = "data/uploads"
    
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    ALLOWED_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "deepseek-chat"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.3
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields like CELERY_BROKER_URL
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse ALLOWED_ORIGINS from environment variable."""
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
            except json.JSONDecodeError:
                pass
            
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        return []

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Log loaded configuration (without sensitive data)
print(f"Environment: {settings.ENVIRONMENT}")
print(f"MongoDB: {settings.MONGODB_URL.split('@')[-1] if '@' in settings.MONGODB_URL else settings.MONGODB_URL}")
print(f"Redis: {settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else settings.REDIS_URL}")
print(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")
