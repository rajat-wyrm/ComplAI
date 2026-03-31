from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    # API Keys
    DEEPSEEK_API_KEY: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(None, env="HUGGINGFACE_API_KEY")
    
    # Database
    MONGODB_URL: str = Field(..., env="MONGODB_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    # Application
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Vector store
    VECTOR_DIMENSION: int = 384
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 5
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env (like DEEPSEEK_API_KEY)
        case_sensitive = True

settings = Settings()
