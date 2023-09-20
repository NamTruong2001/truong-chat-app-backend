from pydantic import BaseModel, conlist
from typing import Union


class CreateGroupChat(BaseModel):
    title: Union[str, None] = None


class GroupMemberIDs(BaseModel):
    member_ids: conlist(int, min_length=1)
