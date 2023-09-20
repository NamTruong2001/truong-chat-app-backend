from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from db import get_db
from sqlalchemy.orm import Session
from schemas.user import UserLoginRequest
from service import auth_login

auth_router = APIRouter()


@auth_router.post("/token", status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user_login_request = UserLoginRequest(username=form_data.username, password=form_data.password)
    login_result = auth_login(user_login_request, db)
    if login_result is not None:
        return login_result
