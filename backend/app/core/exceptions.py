"""
Custom exceptions for the application
"""
from typing import Any, Dict, Optional

class ComplianceException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "COMPLIANCE_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DocumentProcessingError(ComplianceException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DOCUMENT_PROCESSING_ERROR",
            status_code=422,
            details=details
        )

class LLMError(ComplianceException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="LLM_ERROR",
            status_code=503,
            details=details
        )

class RateLimitError(ComplianceException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=429,
            details=details
        )
