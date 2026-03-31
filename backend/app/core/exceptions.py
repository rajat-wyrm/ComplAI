from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': 'Internal server error',
            'detail': str(exc) if isinstance(exc, (ValueError, KeyError, TypeError)) else 'An unexpected error occurred'
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': exc.detail,
            'status_code': exc.status_code
        }
    )

class DocumentProcessingError(Exception):
    pass

class AIAnalysisError(Exception):
    pass

class VectorStoreError(Exception):
    pass
