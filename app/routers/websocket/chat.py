from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from db import get_db
from service import validate_websocket, send_message, authenticate_ws_by_token
from schemas import Message
from dependencies import manager

chat_ws_router = APIRouter()
db: Session = next(get_db())


@chat_ws_router.websocket("/ws2")
async def websocket_endpoint(websocket: WebSocket,
                             client_id: Annotated[int, Depends(authenticate_ws_by_token)]
                             ):
    try:
        if client_id is not None:
            await manager.connect(websocket=websocket, client_id=client_id)
            while True:
                json_payload = await websocket.receive_json()
                message = Message(message=json_payload["message"],
                                  sender_id=client_id,
                                  message_type=json_payload["message_type"],
                                  conversation_id=json_payload["conversation_id"])
                conversation_user_ids, message_response = send_message(message=message, session=db)
                await manager.send_message(message=message_response, sent_to=conversation_user_ids)

    except WebSocketDisconnect as e:
        print(f"{client_id} disconnected")
        manager.disconnect(user_id=client_id)


# @chat_ws_router.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     try:
#         if not validate_websocket(client_id=client_id, token=websocket.headers.get("x-custom-header")):
#             await websocket.accept()
#             await websocket.send_text(data="Validation failed")
#             await websocket.close()
#         else:
#             await manager.connect(websocket=websocket, client_id=client_id)
#             while True:
#                 json_payload = await websocket.receive_json()
#                 message = Message(**json_payload)
#                 conversation_user_ids, message_response = send_message(message=message, session=db)
#                 await manager.send_message(message=message_response, sent_to=conversation_user_ids)
#
#     except WebSocketDisconnect as e:
#         print(f"{client_id} disconnected")
#         manager.disconnect(user_id=client_id)
