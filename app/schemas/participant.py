from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from enums import UserConversationRole
from schemas import UserDTO


class ParticipantDTO(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    type: UserConversationRole
    user: UserDTO

    class Config:
        from_attributes = True
        use_enum_value = True
