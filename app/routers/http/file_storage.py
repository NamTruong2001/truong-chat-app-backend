from typing import Annotated

from global_variables import AZURE_BLOB_STORAGE_URL, azure_container_name
from fastapi import APIRouter, Depends, UploadFile, HTTPException, File, Form
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query
from azure_service import azure_blob_storage_service
from dependencies import auth_service, conversation_service, sio, redis_blob_cache
from schemas import MessageDTO, Attachment, Message

file_router = APIRouter()


@file_router.post(path="/upload-to-conversation")
async def upload_file_to_conversation(file: Annotated[UploadFile, File()],
                                      conversation_id: Annotated[str, Form()],
                                      caption: Annotated[str, Form()],
                                      current_user=Depends(auth_service.get_current_user)):
    (file_type,
     uuid_filename,
     original_file_name) = await azure_blob_storage_service.upload_blob_from_upload_file(file=file)
    attachment = Attachment(file_name=uuid_filename,
                            original_file_name=original_file_name)
    message = Message(sender_id=current_user.id,
                         conversation_id=conversation_id,
                         message_type=file_type,
                         message=caption)

    message_sent_to = conversation_service.persist_message(message=message, attachment=attachment)
    await sio.emit(event="message", room=message_sent_to.conversation_id,
                   data=jsonable_encoder(message_sent_to.message.model_dump()))


    return "Ok"


@file_router.get(path="/g")
async def get_file_sas(file_name = Query(), current_user=Depends(auth_service.get_current_user)):
    return {"url": f"{redis_blob_cache.get(blob_name=file_name)}"}


