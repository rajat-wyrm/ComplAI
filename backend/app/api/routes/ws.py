from fastapi import APIRouter, WebSocket
from app.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    await manager.connect(doc_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(doc_id, websocket)
