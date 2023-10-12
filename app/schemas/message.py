from datetime import datetime
from typing import Union, TypedDict

from enums import MessageEnum
from pydantic import BaseModel


class Attachment(BaseModel):
    file_name: str
    original_file_name: str
    azure_file_url: Union[str, None] = None


class AttachmentDB(Attachment):
    id: int
    message_id: int

class Message(BaseModel):
    sender_id: Union[int, None]
    message: str
    message_type: MessageEnum
    conversation_id: int

    class Config:
        use_enum_value = True


class MessageDTO(Message):
    id: Union[str, None] = None
    created_at: datetime
    attachment: Union[Attachment, None] = None

    class Config:
        from_attributes = True


class SystemMessage(Message):
    pass


class UserJoinGroupMessage(SystemMessage):
    join_user: list[dict]


class MessageSentTo(BaseModel):
    message: Message
    conversation_id: int


