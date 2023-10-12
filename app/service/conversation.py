from datetime import datetime
from typing import Union, Type

import pymongo
from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient
from pymongo.database import Database
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload, selectinload, with_loader_criteria, aliased, Query, defer, load_only, \
    contains_eager
from sqlalchemy import func, and_, distinct, select
from .redis_service import RedisSasBlobCache, ConversationCache
from db import MysqlDBAdapter
from enums import ConversationTypeEnum, UserConversationRole, MessageEnum
from model import ParticipantModel, UserModel, ConversationModel
from schemas import Message, MessageDTO, CreateGroupChat, MessageSentTo, SystemMessage, Attachment, AttachmentDB, \
    ConversationDTO
from validator.exceptions import ConversationNotFound
from mapper import map_message, map_conversation


class ConversationService:
    def __init__(self,
                 redis_sas_cache_service: RedisSasBlobCache,
                 mongo_db_client: MongoClient,
                 redis_message_cache: ConversationCache,
                 db_adapter: MysqlDBAdapter):
        self.db_adapter = db_adapter
        self.mongo_db_client = mongo_db_client
        self.redis_sas_cache_service = redis_sas_cache_service
        self.redis_message_cache = redis_message_cache

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
            new_group_conversation.participants.append(creator_participant)
            session.add(new_group_conversation)
            session.flush()
            session.commit()
            session.refresh(new_group_conversation)

            return new_group_conversation

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

    def paginate_user_conversations(self, current_user: UserModel, page, items_per_page) -> list[ConversationModel]:
        offset = (page - 1) * items_per_page
        with self.db_adapter.get_session() as session:
            conversation_stmt = (
                session.query(ConversationModel).join(ConversationModel.participants)
                .where(ParticipantModel.user_id == current_user.id)
                .limit(items_per_page).offset(offset)
            )
            all_con = conversation_stmt.all()
            return all_con

    def get_all_user_conversation_ids(self, current_user: UserModel):
        with self.db_adapter.get_session() as session:
            ids = session.query(ConversationModel.id).join(ConversationModel.participants).where(
                ParticipantModel.user_id == current_user.id).all()
            return [value for (value,) in ids]

    def get_user_conversation_with_message(self, current_user: UserModel, conversation_page: int,
                                           conversation_items_per_page: int, message_page: int, message_per_page: int):
        conversations: list[ConversationModel] = self.paginate_user_conversations(current_user=current_user,
                                                                                  page=conversation_page,
                                                                                  items_per_page=conversation_items_per_page)
        conversation_dtos: list[ConversationDTO] = []
        for conversation in conversations:
            conversation_dto = map_conversation(conversation)
            conversation_dto.messages = self.get_conversation_messages(conversation_id=conversation.id,
                                                                       page=message_page,
                                                                       items_per_page=message_per_page,
                                                                       current_user=current_user)
            conversation_dtos.append(conversation_dto)

        return conversation_dtos

    def get_conversation_messages(self, conversation_id: int, current_user: UserModel, page: int,
                                  items_per_page: int) -> list[MessageDTO]:
        try:
            exist = self.redis_message_cache.is_user_in_conversation(user_id=current_user.id,
                                                                     conversation_id=conversation_id)
        except ConversationNotFound as e:
            raise HTTPException(detail=e.message, status_code=400)
        if exist is False:
            raise HTTPException(status_code=400, detail="Conversation not found")
        offset = (page - 1) * items_per_page
        messages_collection = self.mongo_db_client.get_database("truong_chat_app").get_collection("messages")
        cursor = (messages_collection.find({"conversation_id": conversation_id})
                  .sort("created_at", pymongo.ASCENDING)
                  .limit(items_per_page)
                  .skip(offset))

        return [map_message(document) for document in cursor]

    # def get_user_conversation_with_first_message(self, current_user: UserModel):
    #     with self.db_adapter.get_session() as session:
    #         subquery = (
    #             session.query(
    #                 MessageModel.conversation_id,
    #                 func.max(MessageModel.created_at).label("latest_created_at")
    #             )
    #             .group_by(MessageModel.conversation_id)
    #             .subquery()
    #         )
    #
    #         conversations_stmt = (
    #             session.query(
    #                 ConversationModel
    #             )
    #             .join(ParticipantModel, ConversationModel.id == ParticipantModel.conversation_id)
    #             .outerjoin(subquery,
    #                        subquery.c.conversation_id == ConversationModel.id)
    #             .outerjoin(MessageModel, MessageModel.created_at == subquery.c.latest_created_at)
    #             .filter(ParticipantModel.user_id == current_user.id)
    #             .options(contains_eager(ConversationModel.messages), selectinload(ConversationModel.participants)
    #                      .selectinload(ParticipantModel.user)
    #                      )
    #             .execution_options(populate_existing=True)
    #         ).order_by(subquery.c.latest_created_at.desc())
    #         results: list[ConversationModel] = conversations_stmt.all()
    #         return results

    # def get_conversation_messages(self, conversation_id: int, current_user: UserModel):
    #     with self.db_adapter.get_session() as session:
    #         user_conversation_stmt: Query = (
    #             session.query(ConversationModel)
    #             .join(ConversationModel.participants)
    #             .filter(ConversationModel.id == conversation_id, ParticipantModel.user_id == current_user.id)
    #         )
    #         user_conversation = user_conversation_stmt.all()
    #         if user_conversation:
    #             get_conversation_message_stmt: Query = (
    #                 session.query(MessageModel)
    #                 .filter(MessageModel.conversation_id == conversation_id)
    #                 .order_by(MessageModel.created_at.desc())
    #             )
    #             return get_conversation_message_stmt.all()
    #         else:
    #             raise HTTPException(detail="Conversation not found", status_code=400)

    # def persist_message(self, message: Message, attachment: Attachment = None) -> MessageSentTo:
    #     with self.db_adapter.get_session() as session:
    #         new_message = MessageModel(**message.model_dump(),
    #                                    created_at=datetime.now())
    #         new_message.attachment = AttachmentModel(original_file_name=attachment.original_file_name,
    #                                                  file_name=attachment.file_name,
    #                                                  ) if attachment is not None else None
    #         if message.message_type != MessageEnum.system:
    #             try:
    #                 is_in = self.redis_message_cache.is_user_in_conversation(user_id=new_message.sender_id,
    #                                                                          conversation_id=new_message.conversation_id)
    #                 if is_in is False:
    #                     raise HTTPException(detail="You are not in the conversation", status_code=400)
    #             except ConversationNotFound as e:
    #                 raise HTTPException(detail=e.message, status_code=400)
    #
    #         session.add(new_message)
    #
    #         session.flush()
    #         session.commit()
    #
    #         attachment_dto: Union[AttachmentDB, None] = None
    #
    #         if new_message.attachment is not None:
    #             attachment_db = new_message.attachment
    #             attachment_dto = AttachmentDB(id=attachment_db.id,
    #                                           message_id=attachment_db.message_id,
    #                                           file_name=attachment_db.file_name,
    #                                           original_file_name=attachment_db.original_file_name,
    #                                           azure_file_url=self.redis_sas_cache_service.get(attachment_db.file_name))
    #
    #         message_response = MessageDB(
    #             **new_message.as_dict(),
    #             attachment=attachment_dto
    #         )
    #         return MessageSentTo(conversation_id=new_message.conversation_id, message=message_response)

    def persist_message(self, message: Message, attachment: Union[Attachment, None] = None) -> MessageSentTo:
        if message.message_type != MessageEnum.system:
            try:
                is_in = self.redis_message_cache.is_user_in_conversation(user_id=message.sender_id,
                                                                         conversation_id=message.conversation_id)
                if is_in is False:
                    raise HTTPException(detail="You are not in the conversation", status_code=400)
            except ConversationNotFound as e:
                raise HTTPException(detail=e.message, status_code=400)

        with self.mongo_db_client.start_session() as session:
            with session.start_transaction():
                try:
                    messages_collection = self.mongo_db_client.get_database("truong_chat_app").get_collection(
                        "messages")
                    message_dto = MessageDTO(**message.model_dump(),
                                             created_at=datetime.now(),
                                             attachment=attachment)
                    inserted_id: ObjectId = (messages_collection
                                             .insert_one(message_dto.model_dump(exclude={"id"})).inserted_id)
                    message_dto.id = str(inserted_id)
                    session.commit_transaction()
                    return MessageSentTo(conversation_id=message_dto.conversation_id, message=message_dto)
                except Exception as e:
                    print(e)
                    session.abort_transaction()
