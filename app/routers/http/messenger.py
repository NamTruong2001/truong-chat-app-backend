from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session
from service import get_current_user_with_db_session, get_user_conversation_with_first_message, \
    get_conversation_messages, \
    find_or_create_private_conversation, create_group_conversation
from schemas import CreateGroupChat, GroupMemberIDs

messenger_router = APIRouter()


@messenger_router.get("/t/{conversation_id}")
async def get_conversation(conversation_id: int, tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    response = get_conversation_messages(conversation_id=conversation_id, db=session, current_user=current_user)
    return response


@messenger_router.get("/conversations")
def conversations(tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
    print(current_user)
    response = get_user_conversation_with_first_message(current_user=current_user, db=session)
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


@messenger_router.post("/conversation/group/add-member")
def add_members_to_group(emp_ids_request: GroupMemberIDs, tu=Depends(get_current_user_with_db_session)):
    current_user, session = tu
