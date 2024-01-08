from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field

class ReadStatusRequest(BaseModel):
    id: Union[int, None]
    user_id: Union[int, None]
    last_seen_message_id: Union[int, None]
    conversation_id: Union[int, None]
    read_at: datetime = Field(default_factory=datetime.utcnow)
