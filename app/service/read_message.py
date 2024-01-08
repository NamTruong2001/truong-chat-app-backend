from fastapi import HTTPException

from db import MysqlDBAdapter
from model.read_status import ReadStatusModel
from schemas.read_status import ReadStatusRequest
from service import ConversationCache
from validator.exceptions import ConversationNotFound


class ReadMessageService:
    def __init__(
        self, mysql_adapter: MysqlDBAdapter, redis_message_cache: ConversationCache
    ):
        self.mysql_adapter = mysql_adapter
        self.redis_message_cache = redis_message_cache

    def update_read_status(self, read_status: ReadStatusRequest):
        try:
            if self.redis_message_cache.is_user_in_conversation(
                user_id=read_status.user_id, conversation_id=read_status.conversation_id
            ):
                raise HTTPException(
                    detail="You are not in the conversation", status_code=400
                )
        except ConversationNotFound as e:
            raise HTTPException(detail=e.message, status_code=400)
        with self.mysql_adapter.get_session() as session:
            # todo
            session.query(ReadStatusModel).where()
