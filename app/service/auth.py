from typing import Annotated, Union, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from db import DBAdapter
from model import UserModel
from schemas import UserInformationResponse, UserLoginRequest, UserForJwtEncode, DecodedJwtUser
from global_variables import JWT_ALGORITHM, JWT_SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    def __init__(self, db_adapter: DBAdapter):
        self.db_adapter = db_adapter

    def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
        with self.db_adapter.get_session() as session:
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
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return DecodedJwtUser(id=decoded_token["id"], username=decoded_token["username"])

    def generate_jwt_token(self, user_db: UserModel):
        user_jwt = UserForJwtEncode(id=user_db.id, username=user_db.username)
        encoded_token = jwt.encode(user_jwt.dict(), JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {"token": encoded_token}

    def auth_login(self, user_login: UserLoginRequest):
        with self.db_adapter.get_session() as session:
            user_db: UserModel = session.query(UserModel).filter(UserModel.username == user_login.username).first()
            if not user_db or user_db.password != user_login.password:
                raise HTTPException(status_code=400, detail="Incorrect username or password")
            return self.generate_jwt_token(user_db=user_db)

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
