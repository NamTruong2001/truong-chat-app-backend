from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.params import Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from model import UserModel
from schemas import UserLoginResponse, UserLoginRequest, UserForJwtEncode

secret_key = "truong"
algorithm = "HS512"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str, db: Session):
    payload = decode_token(token)
    user = db.query(UserModel).filter(UserModel.id == payload["id"]).first()
    return UserLoginResponse(id=user.id, username=user.username)


def authenticate_user(client_name: Annotated[str, Path(alias="client_name")],
                      token: Annotated[str, Depends(oauth2_scheme)] = None) -> str:
    print(client_name)
    print(token)
    try:
        payload = decode_token(token)
        user = UserLoginResponse(id=payload["id"], username=payload["username"])
        if user.username == client_name:
            return user.username
        else:
            raise HTTPException
    except Exception:
        raise HTTPException(status_code=401, detail="Authen error")


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


def validate_websocket(client_id: str, token: str) -> bool:
    if token and client_id == decode_token(token)["username"]:
        return True
    return False
