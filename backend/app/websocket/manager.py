from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, doc_id: str, websocket: WebSocket):
        await websocket.accept()
        if doc_id not in self.active_connections:
            self.active_connections[doc_id] = []
        self.active_connections[doc_id].append(websocket)

    def disconnect(self, doc_id: str, websocket: WebSocket):
        if doc_id in self.active_connections:
            self.active_connections[doc_id].remove(websocket)

    async def send_update(self, doc_id: str, data: dict):
        for ws in self.active_connections.get(doc_id, []):
            await ws.send_json(data)

manager = ConnectionManager()
