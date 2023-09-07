import asyncio
from typing import Annotated, Union
import openai
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.params import Depends, Cookie, Query
from fastapi.middleware.cors import CORSMiddleware
from db import get_db

from model.user import UserModel
from schemas import Message, MessageType, PersonalMessage, ChatRoomMessage, CreateChatroomRequest, \
    JoinChatroomRequest, UserLoginRequest
from service.connection_manager import ConnectionManager
from sqlalchemy.orm import Session
from service.auth import get_current_user, validate_websocket
from routers import auth_router, chat_ws_router, user_router
import random

app = FastAPI()
app.include_router(auth_router)
app.include_router(chat_ws_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_request_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai.api_key}"
}

request_payload = {
    "model": "gpt-3.5-turbo",
    "temperature": 1.0,
    "messages": [
        # {"role": "user", "content": f"Write a fun fact about programmers."},
    ]
}

page_response = {
    "messaging_type": "RESPONSE"
}

manager = ConnectionManager()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/messaging-webhook", status_code=200)
# async def webhook_event(
#         mode: Annotated[str, Query(alias="hub.mode")] = None,
#         token: Annotated[str, Query(alias="hub.verify_token")] = None,
#         challenge: Annotated[int, Query(alias="hub.challenge")] = None,
# ):
#     if mode and token:
#         if mode == 'subscribe' and token == VERIFY_TOKEN:
#             print("WEBHOOK_VERIFIED")
#             return challenge
#     else:
#         raise HTTPException(status_code=403)
#
#
# @app.post("/messaging-webhook", status_code=200)
# async def handle_webhook_event(request: Request):
#     json = await request.json()
#     print(json)
#     if json["object"] == "page":
#         return "EVENT_RECEIVED"
#     raise HTTPException(status_code=404)
#
#
# def send_message_to_openai(messages: list[str]):
#     request_payload["messages"] = messages
#     response = requests.post(OPENAI_TEXT_MESSAGE_URL, headers=openai_request_headers, json=request_payload)
#     json = response.json()
#
#     ai_message_response = json["choices"][0]["text"]
#
#     return ai_message_response
#
#
# def response_to_user(message: str, recipientid: int):
#     page_response["recipient"]["id"] = recipientid
#     page_response["message"]["text"] = message
#     requests.post(url=f"{GRAPH_API}/{APP_ID}/messages?access_token={PAGE_ACCESS_TOKEN}", json=page_response)


async def send_random_numbers():
    while True:
        number = random.randint(1000, 100000)
        await manager.broadcast(Message(
            sender_id="server",
            message=str(number)
        ))
        await asyncio.sleep(2)

# Start sending random numbers concurrently with the WebSocket server
async def startup():
    asyncio.create_task(send_random_numbers())

app.add_event_handler("startup", startup)



@app.post("/create-room", status_code=200)
async def create_chatroom(req: CreateChatroomRequest):
    manager.create_chatroom(admin_id=req.person_id, chatroom_id=req.chatroom_id)


@app.post("/join-room", status_code=200)
async def join_chatroom(req: JoinChatroomRequest):
    await manager.join_chatroom(chatroom_id=req.chatroom_id, user_id=req.person_id)


@app.get("/all-connections")
async def check_all():
    return list(manager.active_connections.keys())



# @app.get("/test")
# def test(request: Request, header: Header):
#     print(request)
#     print(header)
#     return "ok"


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # ssl_keyfile='./0.0.0.0-key.pem',
        # ssl_certfile='./0.0.0.0.pem'
    )
