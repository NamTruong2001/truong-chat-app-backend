from enum import Enum

from pydantic import BaseModel


class Message(BaseModel):
    sender_id: str
    message: str
    type: str = None


class PersonalMessage(Message):
    receiver_id: str


class ChatRoomMessage(Message):
    chatroom_id: str


class MessageType(str, Enum):
    personal = "personal",
    broadcast = "brdcast",
    chatroom = "chatroom"


class CreateChatroomRequest(BaseModel):
    person_id: str
    chatroom_id: str


class JoinChatroomRequest(BaseModel):
    person_id: str
    chatroom_id: str


