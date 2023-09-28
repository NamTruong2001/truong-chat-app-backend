from datetime import datetime
from typing import Union

from enums import MessageEnum
from pydantic import BaseModel


class Message(BaseModel):
    sender_id: Union[int, None]
    message: str
    message_type: MessageEnum
    conversation_id: int

    class Config:
        use_enum_value = True


class MessageCreate(Message):
    pass


class MessageResponse(Message):
    id: int
    created_at: datetime


class SystemMessage(Message):
    pass


class UserJoinGroupMessage(SystemMessage):
    join_user: list[dict]


class MessageSentTo(BaseModel):
    message: Message
    conversation_id: int
