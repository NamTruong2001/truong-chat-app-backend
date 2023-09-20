from starlette.websockets import WebSocket

from schemas.message import Message
from fastapi.encoders import jsonable_encoder


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, client_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, user_id):
        del self.active_connections[user_id]

    def disconnect_websocket(self, websocket: WebSocket):
        socket_list = [self.active_connections[key] for key in self.active_connections]
        socket_list.remove(websocket)

    async def send_message(self, message: Message, sent_to: list[int]):
        try:
            for user_id in sent_to:
                await self.active_connections[user_id].send_json(jsonable_encoder(message))
        except KeyError:
            pass

    async def broadcast(self, message: Message):
        for key in self.active_connections:
            if message.sender_id != key:
                await self.active_connections[key].send_json(
                    {"sender_id": message.sender_id, "content": message.message}
                )
