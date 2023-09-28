from typing import Annotated, Union, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.params import Cookie, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket

from db import get_db, DBAdapter
from model import UserModel
from schemas import UserInformationResponse, UserLoginRequest, UserForJwtEncode, DecodedJwtUser

secret_key = "truong"
algorithm = "HS512"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    def __init__(self, db_adapter: DBAdapter):
        self.db_adapter = db_adapter

    def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
        with self.db_adapter.get_session() as session:
            session.expire_on_commit = False
            try:
                decoded_token: DecodedJwtUser = self.decode_token(token)
                user = session.query(UserModel).filter(UserModel.id == decoded_token.id).one()
                return user
            except NoResultFound:
                raise HTTPException(detail="User not found", status_code=400)
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Token",
                    headers={"WWW-Authenticate": "Bearer"}
                )

    def decode_token(self, token) -> DecodedJwtUser:
        decoded_token = jwt.decode(token, secret_key, algorithms=[algorithm])
        return DecodedJwtUser(id=decoded_token["id"], username=decoded_token["username"])

    def generate_jwt_token(self, user_db: UserModel):
        user_jwt = UserForJwtEncode(id=user_db.id, username=user_db.username)
        encoded_token = jwt.encode(user_jwt.dict(), secret_key, algorithm=algorithm)

        return {"token": encoded_token}

    def auth_login(self, user_login: UserLoginRequest):
        with self.db_adapter.get_session() as session:
            user_db: UserModel = session.query(UserModel).filter(UserModel.username == user_login.username).first()
            if not user_db or user_db.password != user_login.password:
                raise HTTPException(status_code=400, detail="Incorrect username or password")
            return self.generate_jwt_token(user_db=user_db)

    # def validate_websocket(client_id: int, token: str) -> bool:
    #     if token and client_id == decode_token(token)["id"]:
    #         return True
    #     return False
    #
    # async def authenticate_ws_by_token(
    #         self,
    #         websocket: WebSocket,
    #         token: Annotated[Union[str, None], Cookie()] = None,
    #         client_id: Annotated[Union[int, None], Query()] = None,
    # ):
    #     if not validate_websocket(client_id=client_id, token=token):
    #         await websocket.accept()
    #         await websocket.send_text(data="Validation failed")
    #         await websocket.close()
    #         return None
    #     return client_id

    def get_user_token(self, token: str):
        with self.db_adapter.get_session() as session:
            decoded_token: DecodedJwtUser = self.decode_token(token)
            user = session.query(UserModel).filter(UserModel.id == decoded_token.id).one()
            return user

    def authenticate_socketio_connection(self, token: str) -> Optional[UserModel]:
        try:
            user = self.get_user_token(token=token)
            return user
        except:
            return None
