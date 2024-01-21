from http.client import HTTPException

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from socketio import AsyncNamespace

from model import ParticipantModel
from schemas import MessageSentTo, Message
from service import (
    RedisSocketIOManager,
    AuthService,
    ConversationService,
    ParticipantService,
)


class ChatServer(AsyncNamespace):
    def __init__(
        self,
        name_space: str,
        socketio_manager: RedisSocketIOManager,
        auth_service: AuthService,
        conversation_service: ConversationService,
        participant_service: ParticipantService,
    ):
        self.socketio_manager = socketio_manager
        self.auth_service = auth_service
        self.conversation_service = conversation_service
        self.participant_service = participant_service
        super().__init__(name_space)

    async def on_connect(self, sid, auth, environ):
        token = None
        if auth and "HTTP_TOKEN" in auth:
            token = auth["HTTP_TOKEN"]
        # if "HTTP_TOKEN" in environ:
        #     token = environ["HTTP_TOKEN"]
        if token is None:
            raise ConnectionRefusedError("Authentication failed")
        try:
            user_model = self.auth_service.authenticate_socketio_connection(token)
            conversation_ids: list[
                int
            ] = self.conversation_service.get_all_user_conversation_ids(
                current_user=user_model
            )
            participant_in_private_chat: list[
                ParticipantModel
            ] = self.participant_service.get_other_person_in_private_conversation(
                current_user=user_model
            )

            def get_user_online_status(participant_model: ParticipantModel):
                return {
                    "user_id": participant_model.user_id,
                    "conversation_id": participant_model.conversation_id,
                    "online": self.socketio_manager.is_user_online(
                        user_id=participant_model.user_id
                    ),
                }

            online_status = map(get_user_online_status, participant_in_private_chat)
            for con_id in conversation_ids:
                self.enter_room(sid=sid, room=con_id)
            user_id = user_model.id
            await self.save_session(sid, {"user_id": user_id})
            await self.emit(event="presence", to=sid, data=list(online_status))

            if (
                self.socketio_manager.get_number_of_user_connection(user_id=user_id)
                == 0
            ):
                self.socketio_manager.add_online_user_id(user_id=user_id)
                for con_id in conversation_ids:
                    await self.emit(
                        event="presence",
                        room=con_id,
                        skip_sid=sid,
                        data={
                            "conversation_id": con_id,
                            "user": user_model.id,
                            "is_online": True,
                        },
                    )
            self.socketio_manager.add_user_socketio_id_connection(
                user_id=user_id, sid=sid
            )
        except Exception as e:
            print(e)
            return False
        print(f"Client {sid} connected")


    def get_server_instance(self):
        return self

    async def on_disconnect(self, sid):
        print(f"Client {sid} disconnected")
        session = await self.get_session(sid)
        self.socketio_manager.remove_socket_id_from_user(
            user_id=session["user_id"], sid=sid
        )
        if (
            self.socketio_manager.get_number_of_user_connection(
                user_id=session["user_id"]
            )
            == 0
        ):
            for room in self.rooms(sid=sid):
                await self.emit(
                    event="presence",
                    room=room,
                    skip_sid=sid,
                    data={
                        "conversation_id": room,
                        "user": session["user_id"],
                        "online": False,
                    },
                )

    async def on_presence(self, sid, data):
        print(data)

    async def on_read_message(self, sid, message_id):
        try:
            user_session = await self.get_session(sid=sid)
            conversation_to_send: MessageSentTo = (
                self.conversation_service.read_message(
                    message_id=message_id, user_id=user_session["user_id"]
                )
            )
            await self.emit(
                "message",
                room=conversation_to_send.conversation_id,
                data=jsonable_encoder(conversation_to_send.message.model_dump()),
            )
        except ValidationError as ve:
            await self.emit(
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
            await self.emit(event="message", to=sid, data=he.detail)
        except Exception as e:
            print(e)

    async def on_message(self, sid, data):
        print(data)
        user_session = await self.get_session(sid=sid)
        try:
            smessage = Message(**data, sender_id=user_session["user_id"])
            conversation_to_send: MessageSentTo = (
                self.conversation_service.persist_message(message=smessage)
            )
            await self.emit(
                "message",
                room=conversation_to_send.conversation_id,
                data=jsonable_encoder(conversation_to_send.message.model_dump()),
            )
        except ValidationError as ve:
            await self.emit(
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
            await self.emit(event="message", to=sid, data=he.detail)
        except Exception as e:
            print(e)