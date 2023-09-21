import uuid
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from db import get_db
from service import validate_websocket, send_message, authenticate_ws_by_token
from schemas import Message
from dependencies import manager

chat_ws_router = APIRouter()
db: Session = next(get_db())


@chat_ws_router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket,
                             client_id: Annotated[int, Depends(authenticate_ws_by_token)]
                             ):
    connection_uuid = str(uuid.uuid4())
    try:
        if client_id is not None:
            await manager.connect(websocket=websocket, connection_id=connection_uuid, client_id=client_id)
            while True:
                json_payload = await websocket.receive_json()
                message = Message(message=json_payload["message"],
                                  sender_id=client_id,
                                  message_type=json_payload["message_type"],
                                  conversation_id=json_payload["conversation_id"])
                message_response = await send_message(message=message, session=db)
                await manager.send_message(message=message_response.message, sent_to=message_response.sent_to_user_ids)

    except WebSocketDisconnect as e:
        print(f"{client_id} disconnected")
        manager.disconnect(user_id=client_id, connection_id=connection_uuid)

