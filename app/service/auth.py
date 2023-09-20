from typing import Annotated, Union

import jwt
from fastapi import Depends, HTTPException
from fastapi.params import Cookie, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket

from db import get_db
from model import UserModel
from schemas import UserInformationResponse, UserLoginRequest, UserForJwtEncode

secret_key = "truong"
algorithm = "HS512"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user_with_db_session(db: Annotated[Session, Depends(get_db)],
                                     token: Annotated[str, Depends(oauth2_scheme)]) -> (UserModel, Session):
    payload = decode_token(token)
    user = db.query(UserModel).filter(UserModel.id == payload["id"]).first()
    if user is None:
        raise HTTPException(detail="Unauthorized", status_code=401)
    return user, db


def decode_token(token) -> dict:
    decoded_token = jwt.decode(token, secret_key, algorithms=[algorithm])
    return decoded_token


def generate_jwt_token(user_db: UserModel):
    user_jwt = UserForJwtEncode(id=user_db.id, username=user_db.username)
    encoded_token = jwt.encode(user_jwt.dict(), secret_key, algorithm=algorithm)

    return {"token": encoded_token}


def auth_login(user_login: UserLoginRequest, db: Session):
    user_db: UserModel = db.query(UserModel).filter(UserModel.username == user_login.username).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if user_db.password != user_login.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return generate_jwt_token(user_db=user_db)


def validate_websocket(client_id: int, token: str) -> bool:
    if token and client_id == decode_token(token)["id"]:
        return True
    return False


async def authenticate_ws_by_token(
        websocket: WebSocket,
        token: Annotated[Union[str, None], Cookie()] = None,
        client_id: Annotated[Union[int, None], Query()] = None,
):
    if not validate_websocket(client_id=client_id, token=token):
        await websocket.accept()
        await websocket.send_text(data="Validation failed")
        await websocket.close()
        return None
    return client_id
