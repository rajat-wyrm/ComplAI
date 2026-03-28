\"\"\"
Configuration management using Pydantic settings
\"\"\"
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    \"\"\"Application settings\"\"\"
    
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
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
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

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
