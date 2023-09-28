from datetime import datetime
from typing import Optional

from fastapi import HTTPException, Depends
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload, selectinload, with_loader_criteria, aliased, Query, defer, load_only, \
    contains_eager
from sqlalchemy import func, and_, distinct, select

from db import DBAdapter, get_db
from enums import ConversationTypeEnum, UserConversationRole, MessageEnum
from model import ParticipantModel, UserModel, ConversationModel, MessageModel
from schemas import Message, MessageResponse, CreateGroupChat, MessageSentTo, SystemMessage


class ConversationService:
    def __init__(self, db_adapter: DBAdapter):
        self.db_adapter = db_adapter

    def find_conversation_by_two_username(self, username1: str, username2: str):
        with self.db_adapter.get_session() as session:
            usernames = [username1, username2]
            conversations = session.query(ConversationModel) \
                .join(ConversationModel.participants) \
                .join(ParticipantModel.user) \
                .filter(UserModel.username.in_(usernames)) \
                .group_by(ConversationModel.id, ConversationModel.title) \
                .having(func.count(UserModel.username.distinct()) == len(usernames)).first()
            return conversations

    def find_private_conversation_by_2_user_ids(self, user_ids: tuple[int, int]):
        with self.db_adapter.get_session() as session:
            user_id1, user_id2 = user_ids
            conversation = (session.query(ConversationModel)
                            .where(ConversationModel.participants.any(ParticipantModel.user_id == user_id1),
                                   ConversationModel.participants.any(ParticipantModel.user_id == user_id2),
                                   ~ConversationModel.participants.any(~ParticipantModel.user_id.in_(list(user_ids)))
                                   ))

            return conversation.first()

    def create_group_conversation(self,
                                  create_group_chat: CreateGroupChat,
                                  creator: UserModel):
        with self.db_adapter.get_session() as session:
            now_dt = datetime.now()
            new_group_conversation = ConversationModel(**create_group_chat.model_dump(),
                                                       created_at=now_dt,
                                                       updated_at=now_dt,
                                                       creator_id=creator.id,
                                                       type=ConversationTypeEnum.group)
            creator_participant = ParticipantModel(user=creator,
                                                   type=UserConversationRole.creator,
                                                   created_at=now_dt,
                                                   updated_at=now_dt,
                                                   conversation=new_group_conversation)
            session.add(new_group_conversation)
            session.add(creator_participant)

            session.commit()

    def add_user_to_group(self,
                          user_ids: list[int],
                          conversation_id: int,
                          current_user: UserModel,
                          ):
        with self.db_adapter.get_session() as session:
            try:
                now_dt = datetime.now()
                sub_query = (session.query(ParticipantModel.user_id)
                             .where(ParticipantModel.conversation_id == conversation_id)
                             .subquery())
                user_models: list[UserModel] = session.query(UserModel).where(UserModel.id.in_(user_ids),
                                                                              ~UserModel.id.in_(sub_query)).all()
                conversation: ConversationModel = session.query(ConversationModel).join(ParticipantModel).filter(
                    ConversationModel.id == conversation_id, ParticipantModel.user_id == current_user.id).one()
                new_participants: list[ParticipantModel] = [
                    ParticipantModel(conversation=conversation, type=UserConversationRole.member, created_at=now_dt,
                                     updated_at=now_dt, user=user_model) for user_model in user_models]
                conversation.participants.extend(new_participants)
                session.add(conversation)
                session.flush()

                message = SystemMessage(message_type=MessageEnum.system, conversation_id=conversation.id,
                                        sender_id=None,
                                        message=f"{user_models[0].first_name} {user_models[0].last_name}, "
                                                f"and {len(user_models) - 1} others"
                                                f" joined the group.")
                persisted_message = self.persist_message(message=message)

                session.commit()

                return persisted_message
            except NoResultFound:
                raise HTTPException(detail="Conversation not found", status_code=400)

    def find_or_create_private_conversation(self, creator: UserModel, user_id: int):
        with self.db_adapter.get_session() as session:
            try:
                conversation = self.find_private_conversation_by_2_user_ids(user_ids=(creator.id, user_id))
                now_dt = datetime.now()
                if conversation is None:
                    new_conversation = ConversationModel(title=None,
                                                         created_at=now_dt,
                                                         updated_at=now_dt,
                                                         creator_id=creator.id,
                                                         type=ConversationTypeEnum.private
                                                         )
                    session.add(new_conversation)
                    session.flush()
                    member_user: UserModel = session.query(UserModel).filter(UserModel.id == user_id).one()
                    now_dt = datetime.now()
                    participants = [ParticipantModel(
                        type=UserConversationRole.creator,
                        created_at=now_dt,
                        updated_at=now_dt,
                        conversation=new_conversation,
                        user=creator
                    ),
                        ParticipantModel(
                            type=UserConversationRole.member,
                            created_at=now_dt,
                            updated_at=now_dt,
                            conversation=new_conversation,
                            user=member_user
                        )]
                    new_conversation.participants = participants
                    session.add(new_conversation)
                    session.commit()

                    return (session.query(ConversationModel)
                            .filter(ConversationModel.id == new_conversation.id)
                            .options(joinedload(ConversationModel.participants)).first())
                else:
                    return conversation

            except NoResultFound:
                raise HTTPException(detail="Username not found", status_code=400)

    def get_user_conversation_with_first_message(self, current_user: UserModel):
        with self.db_adapter.get_session() as session:
            subquery = (
                session.query(
                    MessageModel.conversation_id,
                    func.max(MessageModel.created_at).label("latest_created_at")
                )
                .group_by(MessageModel.conversation_id)
                .subquery()
            )

            conversations_stmt = (
                session.query(
                    ConversationModel
                )
                .join(ParticipantModel, ConversationModel.id == ParticipantModel.conversation_id)
                .outerjoin(subquery,
                           subquery.c.conversation_id == ConversationModel.id)
                .outerjoin(MessageModel, MessageModel.created_at == subquery.c.latest_created_at)
                .filter(ParticipantModel.user_id == current_user.id)
                .options(contains_eager(ConversationModel.messages), selectinload(ConversationModel.participants)
                         .selectinload(ParticipantModel.user).load_only(UserModel.id,
                                                                        UserModel.username,
                                                                        UserModel.first_name,
                                                                        UserModel.last_name)
                         )
                .execution_options(populate_existing=True)
            ).order_by(subquery.c.latest_created_at.desc())
            results: list[ConversationModel] = conversations_stmt.all()
            return results

    def get_user_conversations(self, current_user: UserModel):
        with self.db_adapter.get_session() as session:
            conversation_stmt = (
                session.query(ConversationModel).join(ConversationModel.participants)
                .where(ParticipantModel.user_id == current_user.id)
            )
            all_con = conversation_stmt.all()
            return all_con

    def get_conversation_messages(self, conversation_id: int, current_user: UserModel):
        with self.db_adapter.get_session() as session:
            user_conversation_stmt: Query = (
                session.query(ConversationModel)
                .join(ConversationModel.participants)
                .filter(ConversationModel.id == conversation_id, ParticipantModel.user_id == current_user.id)
            )
            user_conversation = user_conversation_stmt.all()
            if user_conversation:
                get_conversation_message_stmt: Query = (
                    session.query(MessageModel)
                    .filter(MessageModel.conversation_id == conversation_id)
                    .order_by(MessageModel.created_at.desc())
                )
                return get_conversation_message_stmt.all()
            else:
                raise HTTPException(detail="Conversation not found", status_code=400)

    def persist_message(self, message: Message) -> MessageSentTo:
        with self.db_adapter.get_session() as session:
            new_message = MessageModel(**message.model_dump(), created_at=datetime.now())

            if message.message_type != MessageEnum.system:
                conversation = (
                    session.query(ConversationModel)
                    .filter(
                        ConversationModel.participants.any(ParticipantModel.user_id == message.sender_id),
                        ConversationModel.id == message.conversation_id
                    )
                    .one_or_none()
                )
            else:
                conversation = (
                    session.query(ConversationModel)
                    .filter(ConversationModel.id == message.conversation_id)
                    .one_or_none()
                )
            if conversation is None:
                raise HTTPException(detail="Conversation doesn't exist", status_code=400)

            conversation.messages.append(new_message)
            session.add(conversation)

            session.flush()
            session.commit()
            # db_message: MessageModel = session.get(MessageModel, new_message.id)

            message_response = MessageResponse(
                **new_message.as_dict()
            )
            # session.commit()
            return MessageSentTo(conversation_id=conversation.id, message=message_response)