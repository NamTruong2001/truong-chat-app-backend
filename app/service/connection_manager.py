from starlette.websockets import WebSocket

from schemas.message import Message
from fastapi.encoders import jsonable_encoder


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, dict[str, WebSocket]] = {}

    async def connect(self, client_id: int, connection_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = {}
        self.active_connections[client_id][connection_id] = websocket

    def disconnect(self, user_id: int, connection_id: str):
        del self.active_connections[user_id][connection_id]
        if len(self.active_connections[user_id]) == 0:
            del self.active_connections[user_id]
        print(self.active_connections)

    async def send_message(self, message: Message, sent_to: list[int]):
        try:
            for user_id in sent_to:
                for user_connections in self.active_connections[user_id].values():
                    await user_connections.send_json(jsonable_encoder(message))
        except KeyError:
            pass

    # async def broadcast(self, message: Message):
    #     for key in self.active_connections:
    #         if message.sender_id != key:
    #             await self.active_connections[key].send_json(
    #                 {"sender_id": message.sender_id, "content": message.message}
    #             )
