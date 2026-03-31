from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()

@router.get("/health")
async def health_check(db = Depends(get_database), redis_client = Depends(get_redis)):
    try:
        await db.command('ping')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    try:
        await redis_client.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    return JSONResponse(content={
        'status': 'healthy' if db_status == 'connected' and redis_status == 'connected' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'mongodb': db_status,
            'redis': redis_status,
            'api': 'operational'
        },
        'version': '2.0.0'
    })
