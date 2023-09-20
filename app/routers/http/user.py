from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from model.user import UserModel
from service import get_current_user_with_db_session, signup_new, get_user_info
from db import get_db
from schemas import UserSignUp, UserInformationResponse

user_router = APIRouter()


@user_router.get("/user/me", response_model=UserInformationResponse)
async def get_user(user_session=Depends(get_current_user_with_db_session)):
    user, session = user_session
    return get_user_info(user)


@user_router.post("/signup")
async def signup(sign_up: UserSignUp, db: Session = Depends(get_db)):
    await signup_new(signup=sign_up, db=db)
    return JSONResponse(status_code=200, content="Sign up success")
