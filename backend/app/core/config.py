"""
Configuration management - ULTRA FINAL (BULLETPROOF + PRODUCTION GRADE)
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os
import json
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Ultra robust, zero-crash configuration"""

    # =========================
    # API KEYS (NEVER CRASH)
    # =========================
    OPENAI_API_KEY: Optional[str] = ""
    DEEPSEEK_API_KEY: Optional[str] = ""

    SECRET_KEY: str = "dev-secret"
    ENVIRONMENT: str = "development"

    # =========================
    # DATABASE
    # =========================
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "compliance_copilot"

    # =========================
    # REDIS (OPTIONAL)
    # =========================
    REDIS_URL: Optional[str] = None

    # =========================
    # FILE UPLOAD
    # =========================
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = ".pdf,.docx,.txt"
    UPLOAD_DIR: str = "uploads"

    # =========================
    # CORS + SECURITY
    # =========================
    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # =========================
    # AI SETTINGS
    # =========================
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-4o-mini"

    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.3
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K_RETRIEVAL: int = 3

    # =========================
    # PERFORMANCE
    # =========================
    REQUEST_TIMEOUT: int = 15
    MAX_CONCURRENT_REQUESTS: int = 100

    # =========================
    # LOGGING
    # =========================
    LOG_LEVEL: str = "INFO"

    # =========================
    # CONFIG CORE
    # =========================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

    # =========================
    # VALIDATORS
    # =========================
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        try:
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

        except Exception as e:
            logger.warning(f"Origin parse failed: {e}")

        return ["*"]

    @field_validator("MONGODB_URL", mode="before")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        try:
            if v and not v.startswith("mongodb"):
                logger.warning(f"Invalid MongoDB URL: {v}")
        except:
            pass
        return v


# =========================
# SAFE INIT (NEVER FAIL)
# =========================
try:
    settings = Settings()
except Exception as e:
    logger.error(f"⚠️ Settings failed, fallback mode: {e}")
    settings = Settings(
        OPENAI_API_KEY="",
        DEEPSEEK_API_KEY="",
        SECRET_KEY="fallback-secret"
    )


# =========================
# SAFE DIRECTORY SETUP
# =========================
try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("vectors", exist_ok=True)
except Exception as e:
    logger.warning(f"Directory creation failed: {e}")


# =========================
# SAFE LOGGING (NO UNICODE CRASH)
# =========================
try:
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(
        f"MongoDB: {settings.MONGODB_URL.split('@')[-1] if '@' in settings.MONGODB_URL else 'local'}"
    )
    logger.info(
        f"Redis: {'enabled' if settings.REDIS_URL else 'disabled'}"
    )
    logger.info(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")
except Exception:
    pass


# =========================
# FINAL SAFETY CHECKS
# =========================
if not settings.OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set → using fallback AI")

if not settings.MONGODB_URL:
    logger.error("MONGODB_URL missing → DB may fail")
