from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Query
from fastapi.encoders import jsonable_encoder
from schemas import CreateGroupChat, AddGroupMember, MessageDTO, MessageSentTo
from dependencies import auth_service, conversation_service, sio

messenger_router = APIRouter()


@messenger_router.get("/t/{conversation_id}")
def get_conversation(conversation_id: int, current_user=Depends(auth_service.get_current_user)):
    response = conversation_service.get_conversation_messages(conversation_id=conversation_id,
                                                              current_user=current_user)
    return response


@messenger_router.get("/conversations")
def conversations(current_user=Depends(auth_service.get_current_user)):
    response = conversation_service.get_user_conversation_with_first_message(current_user=current_user)
    return response


@messenger_router.post("/conversation/create")
def new_conversation(user_id: Annotated[int, Query()], current_user=Depends(auth_service.get_current_user)):
    conversation = conversation_service.find_or_create_private_conversation(creator=current_user, user_id=user_id)
    return conversation


@messenger_router.post("/conversation/group", status_code=200)
def create_group_chat(create_group: CreateGroupChat, current_user=Depends(auth_service.get_current_user)):
    conversation_service.create_group_conversation(creator=current_user,
                                                   create_group_chat=create_group)
    return {"message": "Create group chat successfully"}


@messenger_router.post("/conversation/group/add-member", status_code=200)
async def add_members_to_group(add_gr_mem_request: AddGroupMember, current_user=Depends(auth_service.get_current_user)):
    server_message: MessageSentTo = conversation_service.add_user_to_group(user_ids=add_gr_mem_request.member_ids,
                                                                           current_user=current_user,
                                                                           conversation_id=add_gr_mem_request.conversation_id)
    await sio.emit(event="message", room=server_message.conversation_id,
                   data=jsonable_encoder(server_message.message.model_dump()))
    return {"message": "Add user successfully"}
