from datetime import datetime
from pydantic import BaseModel, conlist
from typing import Union
from enums import ConversationTypeEnum
from model import ConversationModel
from .message import MessageDTO
from .participant import ParticipantDTO


class CreateGroupChat(BaseModel):
    title: Union[str, None] = None


class AddGroupMember(BaseModel):
    member_ids: conlist(int, min_length=1)
    conversation_id: int


class DeleteGroupMember(BaseModel):
    member_ids: conlist(int, min_length=1)
    conversation_id: int

class ConversationDTO(BaseModel):
    id: Union[int, None] = None
    title: Union[str, None] = None
    creator_id: int
    created_at: datetime
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    type: ConversationTypeEnum
    messages: list[MessageDTO] = []
    participants: list[ParticipantDTO] = []

    class Config:
        use_enum_value = True