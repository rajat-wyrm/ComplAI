import uuid, logging, traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)

def setup_error_handlers(app):

    @app.exception_handler(HTTPException)
    async def http_handler(request: Request, exc: HTTPException):
        rid = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
        logger.warning(f"[{rid}] HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={
            "error": exc.detail, "status_code": exc.status_code,
            "request_id": rid, "path": str(request.url.path),
        })

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        rid = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
        errs = [{"field": "->".join(str(x) for x in e["loc"]),
                 "message": e["msg"], "type": e["type"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={
            "error": "Validation failed", "details": errs, "request_id": rid,
        })

    @app.exception_handler(IntegrityError)
    async def integrity_handler(request: Request, exc: IntegrityError):
        rid = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
        msg = "Duplicate entry" if "unique" in str(exc.orig).lower() else "Constraint violation"
        return JSONResponse(status_code=409, content={"error": msg, "request_id": rid})

    @app.exception_handler(SQLAlchemyError)
    async def db_handler(request: Request, exc: SQLAlchemyError):
        rid = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
        logger.error(f"[{rid}] DB error: {exc}")
        return JSONResponse(status_code=503, content={"error": "Database unavailable", "request_id": rid})

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        rid = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
        logger.error(f"[{rid}] UNHANDLED: {traceback.format_exc()}")
        return JSONResponse(status_code=500, content={
            "error": "Internal server error", "request_id": rid,
        })
