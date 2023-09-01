from starlette.websockets import WebSocket

from schemas.chat import PersonalMessage, Message, ChatRoomMessage


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.chat_rooms: dict[str, ChatRoom] = {}

    async def connect(self, client_name: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_name] = websocket

    def disconnect(self, user_id):
        del self.active_connections[user_id]

    def disconnect_websocket(self, websocket: WebSocket):
        socket_list = [self.active_connections[key] for key in self.active_connections]
        socket_list.remove(websocket)

    async def send_personal_message(self, message: PersonalMessage):
        for key in self.active_connections:
            if key == message.receiver_id:
                await self.active_connections[key].send_json(
                    {"sender_id": message.sender_id, "content": message.message}
                )

    async def broadcast(self, message: Message):
        for key in self.active_connections:
            if message.sender_id != key:
                await self.active_connections[key].send_json(
                    {"sender_id": message.sender_id, "content": message.message}
                )

    def create_chatroom(self, admin_id, chatroom_id):
        new_chat_room = ChatRoom(admin_id=admin_id, admin_socket=self.active_connections[admin_id])
        self.chat_rooms[chatroom_id] = new_chat_room

    async def join_chatroom(self, chatroom_id, user_id):
        chatroom_ref = self.chat_rooms[chatroom_id]
        chatroom_ref.members[user_id] = self.active_connections[user_id]
        await chatroom_ref.broadcast_message_room(
            message=ChatRoomMessage(message=f"{user_id} join chatroom", sender_id=user_id, chatroom_id=chatroom_id)
        )

    async def send_to_chatroom(self, chatroom_message: ChatRoomMessage):
        chatroom_ref = self.chat_rooms[chatroom_message.chatroom_id]
        await chatroom_ref.broadcast_message_room(chatroom_message)


class ChatRoom:
    admin_id: str
    admin_socket: WebSocket
    members: dict[str, WebSocket]

    def __init__(self, admin_id: str, admin_socket: WebSocket):
        super().__init__()
        self.admin_id = admin_id
        self.admin_socket = admin_socket
        self.members = {admin_id: admin_socket}

    async def broadcast_message_room(self, message: ChatRoomMessage):
        for key in self.members:
            if message.sender_id != key:
                await self.members[key].send_json(
                    {"sender_id": message.sender_id, "content": message.message}
                )
