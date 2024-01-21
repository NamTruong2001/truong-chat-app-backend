from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query

from dependencies import auth_service, conversation_service, sio
from schemas import CreateGroupChat, AddGroupMember, MessageSentTo, DeleteGroupMember

messenger_router = APIRouter()


@messenger_router.get("/t/{conversation_id}")
def get_conversation(
    conversation_id: int,
    page: int = Query(default=1),
    items_per_page: int = Query(default=30),
    current_user=Depends(auth_service.get_current_user),
):
    response = conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        current_user=current_user,
        page=page,
        items_per_page=items_per_page,
    )
    return response


@messenger_router.get("/conversations")
def conversations(
    page: int = Query(default=1, gt=0),
    items_per_page: int = Query(default=30),
    current_user=Depends(auth_service.get_current_user),
):
    response = conversation_service.get_user_conversation_with_preview_message(
        current_user=current_user
        # conversation_page=page,
        # conversation_items_per_page=items_per_page,
        # message_page=page,
        # message_per_page=items_per_page
    )
    return response


@messenger_router.post("/conversation/create")
def new_conversation(
    user_id: Annotated[int, Query()],
    current_user=Depends(auth_service.get_current_user),
):
    conversation = conversation_service.find_or_create_private_conversation(
        creator=current_user, user_id=user_id
    )
    return conversation


@messenger_router.post("/conversation/group", status_code=200)
def create_group_chat(
    create_group: CreateGroupChat, current_user=Depends(auth_service.get_current_user)
):
    new_group = conversation_service.create_group_conversation(
        creator=current_user, create_group_chat=create_group
    )
    return {"message": "Create group chat successfully", "conversation": new_group}


@messenger_router.post("/conversation/group/member", status_code=200)
async def add_members_to_group(
    add_gr_mem_request: AddGroupMember,
    current_user=Depends(auth_service.get_current_user),
):
    server_message: MessageSentTo = conversation_service.add_user_to_group(
        user_ids=add_gr_mem_request.member_ids,
        current_user=current_user,
        conversation_id=add_gr_mem_request.conversation_id,
    )
    await sio.emit(
        namespace="/chat",
        event="message",
        room=server_message.conversation_id,
        data=jsonable_encoder(server_message.message.model_dump()),
    )
    return server_message


@messenger_router.delete("/conversation/group/member", status_code=200)
async def delete_member_from_group(
    delete_members_request: DeleteGroupMember,
    current_user=Depends(auth_service.get_current_user),
):
    (result, server_message) = conversation_service.delete_users_from_group(
        delete_members_request=delete_members_request, current_user=current_user
    )
    await sio.emit(
        namespace="/chat",
        event="message",
        room=server_message.conversation_id,
        data=jsonable_encoder(server_message.message.model_dump()),
    )
    return result
