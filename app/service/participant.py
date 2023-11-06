from sqlalchemy.orm import contains_eager, joinedload

from db import MysqlDBAdapter
from model import UserModel, ConversationModel, ParticipantModel
from enums import ConversationTypeEnum


class ParticipantService:
    def __init__(self, db_adapter: MysqlDBAdapter):
        self.db_adapter = db_adapter

    def get_other_person_in_private_conversation(self, current_user: UserModel):
        with self.db_adapter.get_session() as session:
            conversation_stmt_subquery = (session.query(ConversationModel.id)
                                          .join(ParticipantModel)
                                          .where(ParticipantModel.user_id == current_user.id,
                                                 ConversationModel.type == ConversationTypeEnum.private)
                                          .subquery())
            participant_models = (session.query(ParticipantModel)
                                  .where(ParticipantModel.conversation_id.in_(conversation_stmt_subquery),
                                         ParticipantModel.user_id != current_user.id)
                                  .all())

            return participant_models
