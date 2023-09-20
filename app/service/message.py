from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload, selectinload, with_loader_criteria, aliased, Query, defer, load_only, \
    contains_eager
from sqlalchemy import func, and_, distinct
from enums import ConversationTypeEnum, UserConversationRole
from model import ParticipantModel, UserModel, ConversationModel, MessageModel
from schemas import Message, MessageResponse, CreateGroupChat


def find_conversation_by_two_username(session: Session, username1: str, username2: str):
    usernames = [username1, username2]
    conversations = session.query(ConversationModel) \
        .join(ConversationModel.participants) \
        .join(ParticipantModel.user) \
        .filter(UserModel.username.in_(usernames)) \
        .group_by(ConversationModel.id, ConversationModel.title) \
        .having(func.count(UserModel.username.distinct()) == len(usernames)).first()
    return conversations


def find_private_conversation_by_2_user_ids(session: Session, user_ids: tuple[int, int]):
    user_id1, user_id2 = user_ids
    print(user_id1, user_id2)
    conversation = (session.query(ConversationModel)
                    .where(ConversationModel.participants.any(ParticipantModel.user_id == user_id1),
                           ConversationModel.participants.any(ParticipantModel.user_id == user_id2),
                           ~ConversationModel.participants.any(~ParticipantModel.user_id.in_(list(user_ids)))
                           ))

    return conversation.first()


def create_group_conversation(create_group_chat: CreateGroupChat, creator: UserModel, session: Session):
    try:
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
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500)
    finally:
        session.close()


def add_user_to_group(user_ids: list[int],
                      conversation_id: int,
                      current_user: UserModel,
                      session: Session):
    user_models = (session.query(UserModel)
                   .join(ParticipantModel)
                   .where(UserModel.id.in_(user_ids),
                          ParticipantModel.conversation_id == conversation_id,
                          ))
    ConversationModel.messages.has()


def find_or_create_private_conversation(creator: UserModel, user_id: int, session: Session):
    try:
        conversation = find_private_conversation_by_2_user_ids(session=session, user_ids=(creator.id, user_id))
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
                # conversation_id=new_conversation.id,
                type=UserConversationRole.creator,
                created_at=now_dt,
                updated_at=now_dt,
                conversation=new_conversation,
                user=creator
            ),
                ParticipantModel(
                    # conversation_id=new_conversation.id,
                    type=UserConversationRole.member,
                    created_at=now_dt,
                    updated_at=now_dt,
                    conversation=new_conversation,
                    user=member_user
                )]
            new_conversation.participants = participants
            session.add(new_conversation)
            # session.bulk_save_objects(participants)
            session.commit()

            return (session.query(ConversationModel)
                    .filter(ConversationModel.id == new_conversation.id)
                    .options(joinedload(ConversationModel.participants)).first())
        else:
            return conversation
    except NoResultFound:
        raise HTTPException(detail="Username not found", status_code=400)
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def get_user_conversation_with_first_message(current_user: UserModel, db: Session):
    conversations_stmt: Query = (
        db.query(ConversationModel)
        .join(ParticipantModel)
        .filter(ParticipantModel.user_id == current_user.id)
        .options(selectinload(ConversationModel.messages),
                 selectinload(ConversationModel.participants)
                 .options(contains_eager(ParticipantModel.user).load_only(UserModel.id,
                                                                          UserModel.username,
                                                                          UserModel.first_name,
                                                                          UserModel.last_name))
                 )
    )
    results: list[ConversationModel] = conversations_stmt.all()
    for res in results:
        res.messages = [res.messages[0]]

    return results


def get_conversation_messages(conversation_id: int, current_user: UserModel, db: Session):
    user_conversation_stmt: Query = (
        db.query(ConversationModel)
        .join(ConversationModel.participants)
        .filter(ConversationModel.id == conversation_id, ParticipantModel.user_id == current_user.id)
    )
    user_conversation = user_conversation_stmt.all()
    if user_conversation:
        get_conversation_message_stmt: Query = (
            db.query(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.desc())
        )
        return get_conversation_message_stmt.all()
    else:
        raise HTTPException(detail="Conversation not found", status_code=400)


def send_message(message: Message, session: Session):
    new_message = MessageModel(**message.model_dump(), created_at=datetime.now())

    conversation: ConversationModel = (session.query(ConversationModel)
                                       .where(
        ConversationModel.participants.any(ParticipantModel.user_id == message.sender_id),
        ConversationModel.id == MessageModel.conversation_id).first())

    conversation.messages.append(new_message)
    session.add(conversation)
    session.flush()

    participant_user_id = [participant.user_id for participant in conversation.participants]
    db_message: MessageModel = session.get(MessageModel, new_message.id)
    message_response = MessageResponse(
        **db_message.as_dict()
    )
    session.commit()

    return participant_user_id, message_response
