import socketio
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from socketio import Server
from socketio.exceptions import ConnectionRefusedError

from config import get_settings
from model import ParticipantModel
from schemas import Message, MessageSentTo
from service import (
    AuthService,
    ConversationService,
    RedisSocketIOManager,
    ParticipantService,
)

settings = get_settings()
def ini_socketio(
    socketio_manager: RedisSocketIOManager,
    auth_service: AuthService,
    conversation_service: ConversationService,
    participant_service: ParticipantService,
) -> Server:
    mgr = socketio.AsyncRedisManager(f"redis://{settings.redis_host}:{settings.redis_port}")
    sio = socketio.AsyncServer(
        client_manager=mgr, cors_allowed_origins="*", async_mode="asgi"
    )

    @sio.event
    async def connect(sid, environ, auth):
        token = None
        if auth and "HTTP_TOKEN" in auth:
            token = auth["HTTP_TOKEN"]
        if "HTTP_TOKEN" in environ:
            token = environ["HTTP_TOKEN"]
        if token is None:
            raise ConnectionRefusedError("Authentication failed")
        try:
            user_model = auth_service.authenticate_socketio_connection(token)
            conversation_ids: list[
                int
            ] = conversation_service.get_all_user_conversation_ids(
                current_user=user_model
            )
            participant_in_private_chat: list[
                ParticipantModel
            ] = participant_service.get_other_person_in_private_conversation(
                current_user=user_model
            )

            def get_user_online_status(participant_model: ParticipantModel):
                return {
                    "user_id": participant_model.user_id,
                    "conversation_id": participant_model.conversation_id,
                    "online": socketio_manager.is_user_online(
                        user_id=participant_model.user_id
                    ),
                }

            online_status = map(get_user_online_status, participant_in_private_chat)
            for con_id in conversation_ids:
                sio.enter_room(sid=sid, room=con_id)
            user_id = user_model.id
            await sio.save_session(sid, {"user_id": user_id})
            await sio.emit(event="presence", to=sid, data=list(online_status))

            if socketio_manager.get_number_of_user_connection(user_id=user_id) == 0:
                socketio_manager.add_online_user_id(user_id=user_id)
                for con_id in conversation_ids:
                    await sio.emit(
                        event="presence",
                        room=con_id,
                        skip_sid=sid,
                        data={
                            "conversation_id": con_id,
                            "user": user_model.id,
                            "is_online": True,
                        },
                    )
            socketio_manager.add_user_socketio_id_connection(user_id=user_id, sid=sid)
        except Exception as e:
            print(e)
            return False
        print(f"Client {sid} connected")

    @sio.event
    async def disconnect(sid):
        print(f"Client {sid} disconnected")
        session = await sio.get_session(sid)
        socketio_manager.remove_socket_id_from_user(user_id=session["user_id"], sid=sid)
        if (
            socketio_manager.get_number_of_user_connection(user_id=session["user_id"])
            == 0
        ):
            for room in sio.rooms(sid=sid):
                await sio.emit(
                    event="presence",
                    room=room,
                    skip_sid=sid,
                    data={
                        "conversation_id": room,
                        "user": session["user_id"],
                        "online": False,
                    },
                )

    @sio.event
    async def presence(sid, data):
        print(data)


    @sio.event
    async def read_message(sid, message_id):
        try:
            user_session = await sio.get_session(sid=sid)
            conversation_to_send: MessageSentTo = conversation_service.read_message(
                message_id=message_id, user_id=user_session["user_id"]
            )
            await sio.emit(
                "message",
                room=conversation_to_send.conversation_id,
                data=jsonable_encoder(conversation_to_send.message.model_dump()),
            )
        except ValidationError as ve:
            await sio.emit(
                event="message",
                to=sid,
                data={
                    "error": {
                        "message": "Message validation error",
                        "details": ve.errors(),
                    }
                },
            )
        except HTTPException as he:
            await sio.emit(event="message", to=sid, data=he.detail)
        except Exception as e:
            print(e)

    @sio.event
    async def message(sid, data):
        print(data)
        user_session = await sio.get_session(sid=sid)
        try:
            smessage = Message(**data, sender_id=user_session["user_id"])
            conversation_to_send: MessageSentTo = conversation_service.persist_message(
                message=smessage
            )
            await sio.emit(
                "message",
                room=conversation_to_send.conversation_id,
                data=jsonable_encoder(conversation_to_send.message.model_dump()),
            )
        except ValidationError as ve:
            await sio.emit(
                event="message",
                to=sid,
                data={
                    "error": {
                        "message": "Message validation error",
                        "details": ve.errors(),
                    }
                },
            )
        except HTTPException as he:
            await sio.emit(event="message", to=sid, data=he.detail)
        except Exception as e:
            print(e)

    @sio.event
    def test(sid, room_id, data):
        print(sid, room_id, data)

    return sio
