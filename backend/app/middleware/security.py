import time, uuid, logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        rid = str(uuid.uuid4())[:8]
        request.state.request_id = rid
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"[{rid}] Unhandled: {e}")
            raise
        ms = round((time.time() - start) * 1000, 2)
        response.headers.update({
            "X-Request-ID": rid,
            "X-Response-Time": f"{ms}ms",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        })
        logger.info(f"[{rid}] {request.method} {request.url.path} {response.status_code} {ms}ms")
        return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int = 52_428_800):
        super().__init__(app)
        self.max_bytes = max_bytes
    async def dispatch(self, request: Request, call_next):
        cl = request.headers.get("content-length")
        if cl and int(cl) > self.max_bytes:
            return JSONResponse({"error": "Request too large. Max 50MB."}, status_code=413)
        return await call_next(request)
