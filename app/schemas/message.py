from datetime import datetime
from enums import MessageEnum
from pydantic import BaseModel


class Message(BaseModel):
    sender_id: int
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


class MessageSentTo(BaseModel):
    message: Message
    sent_to_user_ids: list[int]
