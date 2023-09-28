import socketio
from pydantic import ValidationError
from socketio import Server
from db import DBAdapter
from socketio.exceptions import ConnectionRefusedError
from fastapi.encoders import jsonable_encoder
from model import UserModel
from schemas import MessageCreate, MessageSentTo
from service import SocketioIDManager, AuthService, ConversationService


def ini_socketio(db_adapter: DBAdapter,
                 socketio_manager: SocketioIDManager,
                 auth_service: AuthService,
                 conversation_service: ConversationService) -> Server:
    io_db_adapter: DBAdapter = db_adapter
    sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

    @sio.event
    async def connect(sid, environ, auth):
        if 'HTTP_TOKEN' not in environ:
            raise ConnectionRefusedError("Authentication failed")
        try:
            user_model = auth_service.authenticate_socketio_connection(environ["HTTP_TOKEN"])
            user_conversations: list[UserModel] = conversation_service.get_user_conversations(current_user=user_model)
            for con in user_conversations:
                sio.enter_room(sid=sid, room=con.id)
            user_id = user_model.id
            await sio.save_session(sid, {"user_id": user_id})
            socketio_manager.add_user_connection(user_id=user_id, sid=sid)
        except Exception as e:
            print(e)
            return False
        print(f"Client {sid} connected")

    @sio.event
    async def disconnect(sid):
        print(f"Client {sid} disconnected")
        session = await sio.get_session(sid)
        socketio_manager.del_user_connection(user_id=session["user_id"], sid=sid)

    @sio.event
    async def message(sid, data):
        user_session = await sio.get_session(sid=sid)
        try:
            smessage = MessageCreate(**data, sender_id=user_session["user_id"])
            conversation_to_send: MessageSentTo = conversation_service.persist_message(message=smessage)
            await sio.emit("message", room=conversation_to_send.conversation_id, data=jsonable_encoder(conversation_to_send.message.model_dump()))
        except ValidationError as ve:
            await sio.emit(event="message",
                           to=sid,
                           data={"error": {"message": "Message validation error",
                                           "details": ve.errors()}})

    return sio
