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


class CreateMessage(Message):
    pass


class MessageResponse(Message):
    id: int
    created_at: datetime