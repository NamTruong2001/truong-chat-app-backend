from typing import Union
from model import ParticipantModel, ConversationModel
from redis import Redis
from sqlalchemy.orm import selectinload
from db import DBAdapter
from sqlalchemy.exc import NoResultFound
from validator.exceptions import ConversationNotFound


class ConversationCache:
    def __init__(self, db_adapter: DBAdapter, redis_client: Redis):
        self.db_adapter = db_adapter
        self.rc = redis_client
        self.conversation_users_key_template = "conversation:{}:users"

    def is_user_in_conversation(self, user_id: Union[int, str], conversation_id: Union[int, str]) -> bool:
        key = self.conversation_users_key_template.format(conversation_id)
        if not self.is_conversation_cached(conversation_id):
            self.cache_conversation_users(conversation_id, user_id)
        return bool(self.rc.sismember(key, user_id))

    def is_conversation_cached(self, conversation_id: Union[int, str]) -> bool:
        key = self.conversation_users_key_template.format(conversation_id)
        return self.rc.exists(key)

    def cache_conversation_users(self, conversation_id: Union[int, str], user_id: Union[int, str]):
        key = self.conversation_users_key_template.format(conversation_id)
        with self.db_adapter.get_session() as session:
            try:
                conversation: ConversationModel = (session.query(ConversationModel).join(ParticipantModel)
                                                   .where(ParticipantModel.user_id == user_id,
                                                          ConversationModel.id == conversation_id)
                                                   .options(selectinload(ConversationModel.participants))
                                                   .one())
                participants: list[ParticipantModel] = conversation.participants

                user_ids = [participant.user_id for participant in participants]
                self.rc.sadd(key, *user_ids)
                self.rc.expire(key, 1 * 60 * 60)
            except NoResultFound:
                raise ConversationNotFound("Conversation not found!")
