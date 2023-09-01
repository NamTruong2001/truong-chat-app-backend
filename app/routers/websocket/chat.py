from typing import Annotated, Union

from fastapi import APIRouter, WebSocket
from fastapi.params import Cookie, Query, Depends
from service import validate_websocket
from schemas import Message, PersonalMessage, ChatRoomMessage
from service import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


async def get_cookie_or_token(
        websocket: WebSocket,
        token: Annotated[Union[str, None], Cookie()] = None,
        client_id: Annotated[Union[str, None], Query()] = None,
):
    if not validate_websocket(client_id=client_id, token=token):
        await websocket.accept()
        await websocket.send_text(data="Validation failed")
        await websocket.close()
        return None
    return client_id


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             client_id: Annotated[str, Depends(get_cookie_or_token)]
                             ):
    try:
        if client_id is not None:
            await manager.connect(websocket=websocket, client_name=client_id)
            while True:
                json_payload = await websocket.receive_json()
                message = Message(**json_payload)
                print(message.dict())
                if message.type == MessageType.personal:
                    personal_message = PersonalMessage(**json_payload)
                    await manager.send_personal_message(message=personal_message)
                elif message.type == MessageType.broadcast:
                    print(f"{message.sender_id} broadcast a message")
                    brdcast_message = Message(**json_payload)
                    await manager.broadcast(message=brdcast_message)
                elif message.type == MessageType.chatroom:
                    chatroom_message = ChatRoomMessage(**json_payload)
                    print(f"{message.sender_id} send message to {chatroom_message.chatroom_id}")
                    await manager.send_to_chatroom(chatroom_message=chatroom_message)

    except WebSocketDisconnect as e:
        print(f"{client_id} disconnected")
        manager.disconnect(user_id=client_id)
