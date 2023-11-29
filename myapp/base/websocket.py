from typing import List

from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from loguru import logger

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_uuid: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f'websocket {user_uuid} connected')

    def disconnect(self, websocket: WebSocket, user_uuid: str):
        self.active_connections.remove(websocket)
        logger.info(f'websocket {user_uuid} disconnect')

    async def send_message_to_client(self, data: str, user_uuid: str):
        for websocket in self.active_connections:
            if websocket.path_params['user_uuid'] == user_uuid:
                await websocket.send_text(data)
                break
        else:
            logger.warning(f'socket id: {user_uuid} 不存在，忽略本次websocket消息发送： {data}')

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{user_uuid}")
async def websocket_endpoint(websocket: WebSocket, user_uuid: str):
    await manager.connect(websocket, user_uuid)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_uuid)
