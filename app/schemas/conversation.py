from pydantic import BaseModel, conlist
from typing import Union


class CreateGroupChat(BaseModel):
    title: Union[str, None] = None


class AddGroupMember(BaseModel):
    member_ids: conlist(int, min_length=1)
    conversation_id: int
