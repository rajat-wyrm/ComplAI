from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except:
        pass
