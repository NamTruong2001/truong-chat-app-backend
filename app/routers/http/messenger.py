from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session

from model import UserModel
from service import get_current_user_with_db_session, get_user_conversation_with_first_message, \
    get_conversation_messages, \
    find_or_create_private_conversation, create_group_conversation, add_user_to_group
from schemas import CreateGroupChat, AddGroupMember, MessageResponse, MessageSentTo
from dependencies import manager

messenger_router = APIRouter()


@messenger_router.get("/t/{conversation_id}")
async def get_conversation(conversation_id: int, tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    response = get_conversation_messages(conversation_id=conversation_id, db=session, current_user=current_user)
    return response


@messenger_router.get("/conversations")
def conversations(tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    response = get_user_conversation_with_first_message(current_user=current_user, session=session)
    return response


@messenger_router.post("/conversation/create")
def new_conversation(user_id: Annotated[int, Query()], tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    conversation = find_or_create_private_conversation(session=session, creator=current_user, user_id=user_id)
    return conversation


@messenger_router.post("/conversation/group", status_code=200)
def create_group_chat(create_group: CreateGroupChat, tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    create_group_conversation(creator=current_user, session=session, create_group_chat=create_group)


@messenger_router.post("/conversation/group/add-member", status_code=200)
async def add_members_to_group(add_gr_mem_request: AddGroupMember, tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    server_message: MessageSentTo = add_user_to_group(user_ids=add_gr_mem_request.member_ids, session=session,
                                                      current_user=current_user,
                                                      conversation_id=add_gr_mem_request.conversation_id)
    manager.send_message(message=server_message.message, sent_to=server_message.sent_to_user_ids)
    return {"message": "Add user successfully"}
