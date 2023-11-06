from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import auth_service
from schemas.user import UserLoginRequest

auth_router = APIRouter()


@auth_router.post("/token", status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_login_request = UserLoginRequest(
        username=form_data.username, password=form_data.password
    )
    login_result = auth_service.auth_login(user_login_request)
    if login_result is not None:
        return login_result
